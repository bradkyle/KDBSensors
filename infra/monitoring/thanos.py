

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

class Thanos(object):
    def __init__(self, k8s_provider):
        self.grafana_username = "username"
        self.grafana_password = "password"

        self.prometheus_values = """
            rbac:
              create: true

            alertmanager:
              enabled: false

            pushgateway:
              enabled: false

            nodeExporter:
              enabled: false

            kubeStateMetrics:
              enabled: false

            initChownData:
              resources:
                limits:
                  memory: 16Mi
                  cpu: 50m
                requests:
                  memory: 16Mi
                  cpu: 50m

            server:
              extraArgs:
                log.level: debug
                storage.tsdb.min-block-duration: 2h  # Don't change this, see docs/components/sidecar.md
                storage.tsdb.max-block-duration: 2h  # Don't change this, see docs/components/sidecar.md
              retention: 4h
              service:
                annotations:
                   prometheus.io/scrape: "true"
                   prometheus.io/port: "9090"
              statefulSet:
                enabled: true
              podAnnotations:
                prometheus.io/scrape: "true"
                prometheus.io/port: "10902"
              affinity:
                podAntiAffinity:
                  requiredDuringSchedulingIgnoredDuringExecution:
                  - labelSelector:
                      matchExpressions:
                      - key: app
                        operator: In
                        values:
                        - prometheus
                      - key: component
                        operator: In
                        values:
                        - server
                    topologyKey: "kubernetes.io/hostname"
              sidecarContainers:
              - name: thanos-sidecar
                # Always use explicit image tags (release or master-<date>-sha) instead of ambigous `latest` or `master`.
                # Check https://quay.io/repository/thanos/thanos?tab=tags to get latest tag.
                image: quay.io/thanos/thanos:master-2019-11-26-82c005d9
                resources:
                  requests:
                    memory: "4Gi"
                    cpu: "2"
                  limits:
                    memory: "4Gi"
                    cpu: "2"
                env:
                - name: GOOGLE_APPLICATION_CREDENTIALS
                  value: /etc/secret/sa
                args:
                - "sidecar"
                - "--log.level=debug"
                - "--tsdb.path=/data/"
                - "--prometheus.url=http://127.0.0.1:9090"
                - "--objstore.config={type: GCS, config: {bucket: BUCKET_REPLACE_ME}}"
                - "--reloader.config-file=/etc/prometheus-config/prometheus.yml"
                - "--reloader.config-envsubst-file=/etc/prometheus-shared/prometheus.yml"
                - "--reloader.rule-dir=/etc/prometheus-config/rules"
                ports:
                - name: sidecar-http
                  containerPort: 10902
                - name: grpc
                  containerPort: 10901
                - name: cluster
                  containerPort: 10900
                volumeMounts:
                - name: storage-volume
                  mountPath: /data
                - name: thanos-storage-secret
                  mountPath: /etc/secret
                - name: config-volume
                  mountPath: /etc/prometheus-config
                  readOnly: false
                - name: prometheus-config-shared
                  mountPath: /etc/prometheus-shared/
                  readOnly: false
              configPath: /etc/prometheus-shared/prometheus.yml
              replicaCount: 2
              persistentVolume:
                size: 100Gi
              extraVolumes:
              - name: prometheus-config-shared
                emptyDir: {}
              extraVolumeMounts:
              - name: prometheus-config-shared
                mountPath: /etc/prometheus-shared/
              resources:
                limits:
                  cpu: 4
                  memory: 20Gi
                requests:
                  cpu: 4
                  memory: 20Gi
              global:
                scrape_interval: 5s
                scrape_timeout: 4s
                external_labels:
                  prometheus_group: CLUSTER_NAME
                  prometheus_replica: '$(HOSTNAME)'
                evaluation_interval: 5s
              extraSecretMounts:
              - name: thanos-storage-secret
                mountPath: /etc/secret/
                subPath: sa
                readOnly: false
                secretName: thanos-storage-secret

            configmapReload:
              image:
                repository: gcr.io/google-containers/pause-amd64 # This image changed to just pause since there's no option to disable configmapReload container in chart, but thanos-sidecar overtakes this functionality. So basically we don't need another reloader
                tag: 3.1
              resources:
                limits:
                  cpu: 20m
                  memory: 20Mi
                requests:
                  cpu: 20m
                  memory: 20Mi


            serverFiles:
              alerts: {}
              rules: {}
        """

        self.prometheus_chart = k8s.helm.v3.Chart(
            "thanos",
             k8s.helm.v3.ChartOpts(
                chart="",
                fetch_opts=k8s.helm.v3.FetchOpts(
                    repo="https://charts.bitnami.com/bitnami",
                ),
                values=yaml.load(self.values
        )))

