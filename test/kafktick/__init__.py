
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
        ):
        super().__init__('Sensor', name, None, opts)
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.stubs = []
        self.name = name
        self.monitoring_cluster = monitoring_cluster
        self.kafka_operator = kafka_operator

        self.kafka_topic = self.kafka_operator.add_topic(
            name=self.name+"-topic",
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
               name="thorad/hdb",
               base_image="kdb32",
               prefix="hdb",
               path=self.path,
               skip_push=False,
               files=[
                "hdb.q",
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


        # No persistence to log file
        # Create tickerplant consumer
        # The tickerplant listens to updates recieved from the
        # the sensor and dispatches them to the hdb worker and
        # the respective aggregators/cxs
        self.tp_stub = ImageBuilder(
               name="thorad/tickerplant",
               base_image="kdb32",
               prefix="tp",
               path=self.path,
               skip_push=False,
               files=[
                "tick.q",
                "u.q",
                "sym.q"
               ],
               command="q tick.q"
        )
        self.stubs.append(self.tp_stub)


        # TODO different group id per replica
        labels = { 'app': self.name+'-tp-{0}-{1}'.format(get_project(), get_stack()) }
        self.tickerplant = k8s.apps.v1.Deployment('tp-deployment',
            spec=k8s.apps.v1.DeploymentSpecArgs(
                selector=k8s.meta.v1.LabelSelectorArgs(match_labels=producer_labels),
                replicas=1,
                template=k8s.core.v1.PodTemplateSpecArgs(
                    metadata=k8s.meta.v1.ObjectMetaArgs(labels=producer_labels),
                    spec=k8s.core.v1.PodSpecArgs(containers=[
                            k8s.core.v1.ContainerArgs(
                                    name="tp",
                                    image=self.tp_stub.image.image_name,
                                    env=[
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_HOST", value=self.kafka_operator.host),
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_PORT", value=str(self.kafka_operator.port)),
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_TOPIC", value=self.kafka_topic.name),
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_GROUP", value=str(1)),
                                        k8s.core.v1.EnvVarArgs(name="TP_PORT", value=str(self.tp_port)),
                                        k8s.core.v1.EnvVarArgs(name="TP_USER", value=self.tp_user),
                                        k8s.core.v1.EnvVarArgs(name="TP_PASS", value=self.tp_pass)
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

         # // allow external aggregators to subscribe to the tickerplant
        self.tp_service = k8s.core.v1.Service("tp-service-"+self.name,
                spec=k8s.core.v1.ServiceSpecArgs(
                    type='LoadBalancer',
                    selector=labels,
                    ports=[k8s.core.v1.ServicePortArgs(port=self.tp_port)],
        ))

        # Example subsriber
        # The tickerplant listens to updates recieved from the
        # the sensor and dispatches them to the hdb worker and
        # the respective aggregators/cxs
        self.cx_stub = ImageBuilder(
               name="thorad/cx",
               base_image="kdb32",
               prefix="cx",
               path=self.path,
               skip_push=False,
               files=[
                "cx.q",
                "u.q",
                "sym.q"
               ],
               command="q tick.q"
        )
        self.stubs.append(self.cx_stub)


        # TODO different group id per replica
        labels = { 'app': self.name+'-cx-{0}-{1}'.format(get_project(), get_stack()) }
        self.tickerplant = k8s.apps.v1.Deployment('cx-deployment',
            spec=k8s.apps.v1.DeploymentSpecArgs(
                selector=k8s.meta.v1.LabelSelectorArgs(match_labels=producer_labels),
                replicas=1,
                template=k8s.core.v1.PodTemplateSpecArgs(
                    metadata=k8s.meta.v1.ObjectMetaArgs(labels=producer_labels),
                    spec=k8s.core.v1.PodSpecArgs(containers=[
                            k8s.core.v1.ContainerArgs(
                                    name="cx",
                                    image=self.cx_stub.image.image_name,
                                    env=[
                                        k8s.core.v1.EnvVarArgs(name="TP_PORT", value=str(self.tp_port)),
                                        k8s.core.v1.EnvVarArgs(name="TP_USER", value=self.tp_user),
                                        k8s.core.v1.EnvVarArgs(name="TP_PASS", value=self.tp_pass)
                                    ],
                                    ports=[k8s.core.v1.ContainerPortArgs(
                                        container_port=8080,
                                    )],
                                    resources=k8s.core.v1.ResourceRequirementsArgs(
                                        requests={
                                            "cpu": "100m",
                                            "memory": "100m",
                                        },
                                    ),
                           ),
                      ]),
                ),
            ),
        )

         # // allow external aggregators to subscribe to the tickerplant
        self.cx_service = k8s.core.v1.Service("cx-service-"+self.name,
                spec=k8s.core.v1.ServiceSpecArgs(
                    type='LoadBalancer',
                    selector=labels,
                    ports=[k8s.core.v1.ServicePortArgs(port=self.tp_port)],
        ))


    def clean(self):
        for s in self.stubs:
            print(s.dockerfile_path)


