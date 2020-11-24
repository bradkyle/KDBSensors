
import json
from typing import Mapping, Sequence, List
import pulumi
import uuid

import pulumi_docker as docker
import pulumi_gcp as gcp
import pulumi_kubernetes as k8s
from pulumi import Config, export, get_project, get_stack, Output, ResourceOptions
from pulumi_random import RandomPassword
from pulumi import get_stack, ResourceOptions, StackReference
import pulumi

from grafanalib.core import (
    Alert, AlertCondition, Dashboard, Graph,
    GreaterThan, OP_AND, OPS_FORMAT, Row, RTYPE_SUM, SECONDS_FORMAT,
    SHORT_FORMAT, single_y_axis, Target, TimeRange, YAxes, YAxis
)

class MonitoringCluster(pulumi.ComponentResource):
    def __init__(self):

        self.primary_node_count = 1
        self.master_version = 1
        self.cluster_password = RandomPassword("monitoring_cluster_password", length=20, special=True).result
        self.cluster_username = 'admin'
        self.node_machine_type = 'n1-standard-1'

        # TODO Deploy pulumi stacks in kubernetes
        # Instantiate a new kubernetes cluster for  
        # management of the training cycle
        self.k8s_cluster = gcp.container.Cluster('monitoring',
            initial_node_count=self.primary_node_count,
            node_version=self.master_version,
            min_master_version=self.master_version,
            master_auth=gcp.container.ClusterMasterAuthArgs(username=self.cluster_username, password=self.cluster_password),
            node_config=gcp.container.ClusterNodeConfigArgs(
                machine_type=self.node_machine_type,
                oauth_scopes=[
                    'https://www.googleapis.com/auth/compute',
                    'https://www.googleapis.com/auth/devstorage.read_only',
                    'https://www.googleapis.com/auth/logging.write',
                    'https://www.googleapis.com/auth/monitoring'
                ],
            ),
        )

        # Manufacture a GKE-style Kubeconfig. Note that this is slightly "different" because of the way GKE requires
        # gcloud to be in the picture for cluster authentication (rather than using the client cert/key directly).
        self.k8s_info = Output.all(self.k8s_cluster.name, self.k8s_cluster.endpoint, self.k8s_cluster.master_auth)
        self.k8s_config = self.k8s_info.apply(
            lambda info: """apiVersion: v1
                clusters:
                - cluster:
                    certificate-authority-data: {0}
                    server: https://{1}
                  name: {2}
                contexts:
                - context:
                    cluster: {2}
                    user: {2}
                  name: {2}
                current-context: {2}
                kind: Config
                preferences: {{}}
                users:
                - name: {2}
                  user:
                    auth-provider:
                      config:
                        cmd-args: config config-helper --format=json
                        cmd-path: gcloud
                        expiry-key: '{{.credential.token_expiry}}'
                        token-key: '{{.credential.access_token}}'
                      name: gcp
        """.format(info[2]['clusterCaCertificate'], info[1], '{0}_{1}_{2}'.format(project, zone, info[0])))

        # Make a Kubernetes provider instance that uses our cluster from above.
        self.k8s_provider = k8s.Provider('gke_monitoring_k8s', kubeconfig=self.k8s_config)

        self.thanos_config = """
        objstoreConfig: |-
              type: s3
              config:
                bucket: thanos
                endpoint: {{ include "thanos.minio.fullname" . }}.monitoring.svc.cluster.local:9000
                access_key: minio
                secret_key: KEY
                insecure: true
            querier:
              stores:
                - SIDECAR-SERVICE-IP-ADDRESS-1:10901
                - SIDECAR-SERVICE-IP-ADDRESS-2:10901
            bucketweb:
              enabled: true
            compactor:
              enabled: true
            storegateway:
              enabled: true
            ruler:
              enabled: true
              alertmanagers:
                - http://prometheus-operator-alertmanager.monitoring.svc.cluster.local:9093
              config: |-
                groups:
                  - name: "metamonitoring"
                    rules:
                      - alert: "PrometheusDown"
                        expr: absent(up{prometheus="monitoring/prometheus-operator"})
            minio:
              enabled: true
              accessKey:
                password: "minio"
              secretKey:
                password: "KEY"
              defaultBuckets: "thanos"
        """
        # Add Monitoring Prometheus
        # Install the Prometheus Operator in the data producer
        # Inject prometheus chart into kubernetes cluster
        self.thanos_chart = Chart(
            "thanos",
            ChartOpts(
                chart="thanos",
                # version="1.24.4",
                fetch_opts=FetchOpts(
                    repo="https://charts.bitnami.com/bitnami",
                ),
                values={

                }
            ),
        )

        # self.grafana_username = "username"
        # self.grafana_password = "password"

        # # TODO password, username etc
        self.grafana_chart = Chart(
            "grafana",
            ChartOpts( # TODO add bitnami/grafana
                chart="grafana",
                version="3.4.7",
                fetch_opts=FetchOpts(
                    repo="https://charts.bitnami.com/bitnami",
                ),
                values={
                    "service":{
                        "type":"LoadBalancer"
                    },
                    "admin":{
                        "username":self.grafana_username,
                        "password":self.grafana_password
                    },
                    "plugins":[],
                    "dashboardConfigMaps":{},
                }
            ),
        )

    def inject_prometheus(self, label, k8s_provider):
        k8s.helm.v3.Chart(
            "prometheus-operator",
             k8s.helm.v3.ChartOpts(
                chart="prometheus-operator",
                # version="1.24.4",
                fetch_opts=k8s.helm.v3.FetchOpts(
                    repo="https://charts.bitnami.com/bitnami",
                ),
                values={
                    "prometheus": {
                        "thanos": {
                            "create": True,
                            "service":{
                                "type": "LoadBalancer"
                            }
                        },
                        "service": {
                            "type":"ClusterIp",
                        },
                        "externalLabels":{
                            "cluster": label
                        }
                    },
                    "operator":{
                        "service":{
                            "type":"ClusterIp"
                        }
                    },
                    "alertmanager":{
                        "service":{
                            "type":"ClusterIp"
                        }
                    }
                }
            ),
            opts=ResourceOptions(provider=k8s_provider))

    def add_service_monitor(self, name:str, labels, namespace:str, interval:str, provider):
        exposed_service = Service("exposed-service-"+name,
                spec=ServiceSpecArgs(
                    type='Service',
                    selector=labels,
                    ports=[ServicePortArgs(port=port)],
                ), __opts__=ResourceOptions(provider=k8s_provider))

        service_monitor = Service("service-monitor-"+name,
                spec=ServiceSpecArgs(
                    type='ServiceMonitor',
                    selector=labels,
                    ports=[ServicePortArgs(port=port)],
                ), __opts__=ResourceOptions(provider=k8s_provider))


    def add_grafana_dashboard(self, dashboard, columns_per_row=2):
        pass

    def add_grafana_dashboard_graph(self, dashboard, graph):
        pass



















