import os
import pulumi
import pulumi_docker as docker
import pulumi_gcp as gcp
import pulumi_kubernetes as k8s
from infra.docker.docker import ImageBuilder

class KDBIngestCanary(pulumi.ComponentResource):
    """
    Creates a simple KDB instance to check that kafka reading etc
    is working correctly with kdb
    """
    def __init__(self, kafka_host, kafka_port, kafka_topic):
        self.kafka_host = kafka_host
        self.kafka_port = kafka_port
        self.kafka_topic = kafka_topic
        self.path = os.path.dirname(os.path.abspath(__file__))

        producer_labels = {
            "app": "producer",
            "tier": "ingress",
            "role": "master"
        }

        self.producer_stub = ImageBuilder(
               name="producer",
               base_image="kdb32",
               prefix="producer",
               path=self.path,
               files=[
                "producer.q"
               ],
               command="q producer.q -p 8080"
        )

        self.producer_deployment = k8s.apps.v1.Deployment('producer-deployment',
            spec=k8s.apps.v1.DeploymentSpecArgs(
                selector=k8s.meta.v1.LabelSelectorArgs(match_labels=producer_labels),
                replicas=1,
                template=k8s.core.v1.PodTemplateSpecArgs(
                    metadata=k8s.meta.v1.ObjectMetaArgs(labels=producer_labels),
                    spec=k8s.core.v1.PodSpecArgs(containers=[
                            k8s.core.v1.ContainerArgs(
                                    name="producer",
                                    image=self.producer_stub.image.image_name,
                                    env=[
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_HOST", value=self.kafka_host),
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_PORT", value=str(kafka_port)),
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_TOPIC", value=self.kafka_topic)
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

        consumer_labels = {
            "app": "producer",
            "tier": "ingress",
            "role": "master"
        }

        self.consumer_stub = ImageBuilder(
               name="consumer",
               base_image="kdb32",
               prefix="consumer",
               path=self.path,
               files=[
                "consumer.q"
               ],
               command="q consumer.q -p 8080"
        )

        self.consumer_deployment = k8s.apps.v1.Deployment('consumer-deployment',
            spec=k8s.apps.v1.DeploymentSpecArgs(
                selector=k8s.meta.v1.LabelSelectorArgs(match_labels=consumer_labels),
                replicas=1,
                template=k8s.core.v1.PodTemplateSpecArgs(
                    metadata=k8s.meta.v1.ObjectMetaArgs(labels=consumer_labels),
                    spec=k8s.core.v1.PodSpecArgs(containers=[
                            k8s.core.v1.ContainerArgs(
                                    name="consumer",
                                    image=self.consumer_stub.image.image_name,
                                    env=[
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_HOST", value=self.kafka_host),
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_PORT", value=str(self.kafka_port)),
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_TOPIC", value=self.kafka_topic)
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


class PYIngestCanary(pulumi.ComponentResource):
    """
    Creates a simple KDB instance to check that kafka reading etc
    is working correctly with kdb
    """
    def __init__(self,name,kafka_operator):
        self.name = name
        self.kafka_operator = kafka_operator
        self.kafka_host = kafka_operator.host
        self.kafka_port = kafka_operator.port
        self.kafka_topic = self.name + "-topic"
        self.path = os.path.dirname(os.path.abspath(__file__))

        self.kafka_operator.add_topic(
              name=self.kafka_topic,
        )

        producer_labels = {
            "app": "producer",
            "tier": "ingress",
            "role": "master"
        }

        self.producer_stub = ImageBuilder(
               name="producer",
               base_image="python:3.8.6-slim-buster",
               prefix="producer",
               path=self.path,
               files=[
                "producer.py",
                "requirements.txt"
               ],
               precmd_run = [
                    "pip install -r requirements.txt"
               ],
               command="producer.py"
        )

        self.producer_deployment = k8s.apps.v1.Deployment('producer-deployment',
            spec=k8s.apps.v1.DeploymentSpecArgs(
                selector=k8s.meta.v1.LabelSelectorArgs(match_labels=producer_labels),
                replicas=1,
                template=k8s.core.v1.PodTemplateSpecArgs(
                    metadata=k8s.meta.v1.ObjectMetaArgs(labels=producer_labels),
                    spec=k8s.core.v1.PodSpecArgs(containers=[
                            k8s.core.v1.ContainerArgs(
                                    name="producer",
                                    image=self.producer_stub.image.image_name,
                                    env=[
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_HOST", value=self.kafka_host),
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_PORT", value=str(self.kafka_port)),
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_TOPIC", value=self.kafka_topic)
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

        consumer_labels = {
            "app": "consumer",
            "tier": "ingress",
            "role": "master"
        }

        self.consumer_stub = ImageBuilder(
               name="consumer",
               base_image="python:3.8.6-slim-buster",
               prefix="consumer",
               path=self.path,
               files=[
                "consumer.py",
                "requirements.txt"
               ],
               precmd_run = [
                    "pip install -r requirements.txt"
               ],
               command="consumer.py"
        )

        self.consumer_deployment = k8s.apps.v1.Deployment('consumer-deployment',
            spec=k8s.apps.v1.DeploymentSpecArgs(
                selector=k8s.meta.v1.LabelSelectorArgs(match_labels=consumer_labels),
                replicas=1,
                template=k8s.core.v1.PodTemplateSpecArgs(
                    metadata=k8s.meta.v1.ObjectMetaArgs(labels=consumer_labels),
                    spec=k8s.core.v1.PodSpecArgs(containers=[
                            k8s.core.v1.ContainerArgs(
                                    name="consumer",
                                    image=self.consumer_stub.image.image_name,
                                    env=[
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_HOST", value=self.kafka_host),
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_PORT", value=str(self.kafka_port)),
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_TOPIC", value=self.kafka_topic),
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

