
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
import yaml

from grafanalib.core import (
    Alert, AlertCondition, Dashboard, Graph,
    GreaterThan, OP_AND, OPS_FORMAT, Row, RTYPE_SUM, SECONDS_FORMAT,
    SHORT_FORMAT, single_y_axis, Target, TimeRange, YAxes, YAxis
)

# https://docs.bitnami.com/tutorials/create-multi-cluster-monitoring-dashboard-thanos-grafana-prometheus/

class MonitoringOperator(object):
    def __init__(self, k8s_provider):
        self.grafana_username = "username"
        self.grafana_password = "password"

        # Add Monitoring Prometheus
        # Install the Prometheus Operator in the data producer
        # Inject prometheus chart into kubernetes cluster
        # self.prometheus_chart = k8s.helm.v3.Chart(
        #     "prometheus",
        #      k8s.helm.v3.ChartOpts(
        #         chart="prometheus",
        #         fetch_opts=k8s.helm.v3.FetchOpts(
        #             repo="https://charts.helm.sh/stable",
        #         ),
        # ))

        # self.prometheus_chart = k8s.helm.v3.Chart(
        #     "prometheus",
        #      k8s.helm.v3.ChartOpts(
        #         chart="kube-prometheus-stack",
        #         fetch_opts=k8s.helm.v3.FetchOpts(
        #             repo="https://prometheus-community.github.io/helm-charts",
        #         ),
        # ))

        self.thanos_chart = k8s.helm.v3.Chart(
            "thanos",
             k8s.helm.v3.ChartOpts(
                chart="thanos",
                fetch_opts=k8s.helm.v3.FetchOpts(
                    repo="https://charts.bitnami.com/bitnami",
                ),
        ))

        # # TODO password, username etc
        self.grafana_chart = k8s.helm.v3.Chart(
            "grafana",
            k8s.helm.v3.ChartOpts( # TODO add bitnami/grafana
                chart="grafana",
                version="3.4.7",
                fetch_opts=k8s.helm.v3.FetchOpts(
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


    def add_service_monitor(self, name:str, labels, namespace:str, interval:str, port=8080, k8s_provider=None):
        exposed_service = k8s.core.v1.Service("exposed-service-"+name,
                spec=k8s.core.v1.ServiceSpecArgs(
                    type='Service',
                    selector=labels,
                    ports=[k8s.core.v1.ServicePortArgs(port=port)],
                ), __opts__=ResourceOptions(provider=k8s_provider))

        service_monitor = k8s.core.v1.Service("service-monitor-"+name,
                spec=k8s.core.v1.ServiceSpecArgs(
                    type='ServiceMonitor',
                    selector=labels,
                    ports=[k8s.core.v1.ServicePortArgs(port=port)],
                ), __opts__=ResourceOptions(provider=k8s_provider))


    def add_grafana_dashboard(self, dashboard, columns_per_row=2):
        pass

    def add_grafana_dashboard_graph(self, dashboard, graph):
        pass


