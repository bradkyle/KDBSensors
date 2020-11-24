import os
import pulumi
import pulumi_docker as docker
import pulumi_gcp as gcp
import pulumi_kubernetes as k8s
from infra.docker import ImageBuilder

class KDBAgent(pulumi.ComponentResource):
    """
    Creates a simple KDB instance to check that kafka reading etc
    is working correctly with kdb
    """
    def __init__(self, kafka_host, kafka_port, kafka_topic):
        self.kafka_host = kafka_host
        self.kafka_port = kafka_port
        self.kafka_topic = kafka_topic
        self.path = os.path.dirname(os.path.abspath(__file__))

        self.effector_stub = ImageBuilder(
               name="canary_producer",
               base_image="kdb32",
               prefix="producer",
               path=self.path,
               files=[
                "producer.q"
               ],
               command="q producer.q -p 8080"
        )

        self.producer_deployment = k8s.apps.v1.Deployment('producer_deployment',
            spec=k8s.apps.v1.DeploymentSpecArgs(
                selector=k8s.meta.v1.LabelSelectorArgs(match_labels=producer_labels),
                replicas=1,
                template=k8s.core.v1.PodTemplateSpecArgs(
                    metadata=k8s.meta.v1.ObjectMetaArgs(labels=producer_labels),
                    spec=k8s.core.v1.PodSpecArgs(containers=[
                            k8s.core.v1.ContainerArgs(
                                    name="state",
                                    image=self.producer_stub.image.image_name,
                                    env=[
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_HOST", value=kafka_host),
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_PORT", value=kafka_port),
                                        k8s.core.v1.EnvVarArgs(name="KAFKA_TOPIC", value=kafka_topic)
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
                            k8s.core.v1.ContainerArgs(
                                    name="model",
                                    image=self.producer_stub.image.image_name,
                                    env=[
                                        k8s.core.v1.EnvVarArgs(name="STATE_PORT", value=kafka_host),
                                        k8s.core.v1.EnvVarArgs(name="ADAPT_PORT", value=kafka_host),
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
                           k8s.core.v1.ContainerArgs(
                                    name="adapter",
                                    image=self.producer_stub.image.image_name,
                                    env=[

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

