
import os
import pulumi
import pulumi_docker as docker
import pulumi_gcp as gcp
import pulumi_kubernetes as k8s
from infra.docker import ImageBuilder
from pulumi import Config, export, get_project, get_stack, Output, ResourceOptions
import pulumi_random as prand
from typing import Mapping, Sequence

# https://github.com/weaveworks/grafanalib
# Used for building grafana dashboards dynamically
from grafanalib.core import (
    Alert, AlertCondition, Dashboard, Graph,
    GreaterThan, OP_AND, OPS_FORMAT, Row, RTYPE_SUM, SECONDS_FORMAT,
    SHORT_FORMAT, single_y_axis, Target, TimeRange, YAxes, YAxis
)

# aggregator reads from topic
class AddAgg(self):
    def __init__(self):
        pass

class SensorSpec(object):
    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.symfile = ""
        self.sensor_image = None

class Sensor(pulumi.ComponentResource):
    def __init__(self,
                 name:str = "sensor",
                 monitoring_cluster = None,
                 kafka_operator = None,
                 opts:pulumi.ResourceOptions = None,
                 sensor_stub = None
        ):
        super().__init__('Sensor', name, None, opts)
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.stubs = []
        self.name = name
        self.monitoring_cluster = monitoring_cluster
        self.kafka_operator = kafka_operator

        # TODO make configurable
        self.kafka_topic = self.kafka_operator.add_topic(
            name=self.name+"-topic",
            replicas=3,
            partitions=10,
            retention_ms=3.6e6,
            segment_bytes=1e9,
            retention_bytes=1e9
        )

        self.tp_user = prand.RandomString("tp_user-"+self.name,length=10,special=False);
        self.tp_pass = prand.RandomPassword("tp_pass-"+self.name,length=16,special=True);
        self.tp_port = 5000;
        self.pull_policy = "IfNotPresent"

        # The sensor can be of any image format
        # which would allow for the tickerplant and
        # hdb to act as a sidecar therin
        self.sensor_stub = ImageBuilder(
               name="thorad/sensor",
               base_image="kdb32",
               prefix="sensor",
               path=self.path,
               skip_push=False,
               files=[
                "sensor.q"
               ],
               command="q sensor.q"
        )
        self.stubs.append(self.sensor_stub)


        self.sensor_deployment = k8s.apps.v1.Deployment('sensor-deployment',
            spec=k8s.apps.v1.DeploymentSpecArgs(
                selector=k8s.meta.v1.LabelSelectorArgs(match_labels=producer_labels),
                replicas=1,
                template=k8s.core.v1.PodTemplateSpecArgs(
                    metadata=k8s.meta.v1.ObjectMetaArgs(labels=producer_labels),
                    spec=k8s.core.v1.PodSpecArgs(containers=[
                            k8s.core.v1.ContainerArgs(
                                    name="sensor",
                                    image=self.producer_stub.image.image_name,
                                    env=[
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_HOST", value=self.kafka_operator.host),
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_PORT", value=str(self.kafka_operator.port)),
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_TOPIC", value=self.kafka_topic.name)
                                    ],
                                    ports=[k8s.core.v1.ContainerPortArgs(
                                        container_port=8080,
                                    )],
                                    resources=k8s.core.v1.ResourceRequirementsArgs(
                                        requests={
                                            "cpu": "100m",
                                            "memory": "100Mi",
                                        },
                                    ),
                           ),
                      ]),
                ),
            ),
        )

        # Create hdb writer 
        # The tickerplant listens to updates recieved from the
        # the sensor and dispatches them to the hdb worker and
        # the respective aggregators/cxs
        self.sink_stub = ImageBuilder(
               name="thorad/sink",
               base_image="kdb32",
               prefix="sink",
               path=self.path,
               skip_push=False,
               files=[
                "sink.q",
                "u.q",
               ],
               command="q sink.q"
        )
        self.stubs.append(self.sink_stub)

        # Should write to raw and one dir per other datum kind

        # TODO same group id per replica
        self.sink_deployment = k8s.apps.v1.Deployment('sink-deployment',
            spec=k8s.apps.v1.DeploymentSpecArgs(
                selector=k8s.meta.v1.LabelSelectorArgs(match_labels=producer_labels),
                replicas=1,
                template=k8s.core.v1.PodTemplateSpecArgs(
                    metadata=k8s.meta.v1.ObjectMetaArgs(labels=producer_labels),
                    spec=k8s.core.v1.PodSpecArgs(containers=[
                            k8s.core.v1.ContainerArgs(
                                    name="sink",
                                    image=self.sink_stub.image.image_name,
                                    env=[
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_HOST", value=self.kafka_operator.host),
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_PORT", value=str(self.kafka_operator.port)),
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_TOPIC", value=self.kafka_topic.name),
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_GROUP", value=str(0))
                                    ],
                                    ports=[k8s.core.v1.ContainerPortArgs(
                                        container_port=8080,
                                    )],
                                    resources=k8s.core.v1.ResourceRequirementsArgs(
                                        requests={
                                            "cpu": "100m",
                                            "memory": "100Mi",
                                        },
                                    ),
                           ),
                      ]),
                ),
            ),
        )


        # TODO dispatcher / rdb


