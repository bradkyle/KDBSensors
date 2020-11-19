

import pulumi
import pulumi_docker as docker
import pulumi_gcp as gcp
import pulumi_kubernetes as k8s
from infra.docker import ImageBuilder

class KDBIngestCanary(pulumi.ComponentResource):
    """
    Creates a simple KDB instance to check that kafka reading etc
    is working correctly with kdb
    """
    def __init__(self, kafka_host, kafka_port, kafka_topic):
        self.kafka_host = kafka_host
        self.kafka_port = kafka_port
        self.kafka_topic = kafka_topic

        self.producer_stub = ImageBuilder(
               name="canary_producer",
               base_image="kdb32",
               files=[
                "producer.q"
               ],
        )

        self.producer_deployment = Deployment('kdb_ingest_canary_deployment',
            spec=DeploymentSpecArgs(
                # selector=LabelSelectorArgs(match_labels=labels),
                replicas=1,
                template=PodTemplateSpecArgs(
                    # metadata=ObjectMetaArgs(labels=labels),
                    spec=PodSpecArgs(containers=[
                            k8s.core.v1.ContainerArgs(
                                    name="tickerplant",
                                    image=self.producer_stub.image.image_name,
                                    env=[
                                        {"name":"KAFKA_HOST", "value":kafka_host},
                                        {"name":"KAFKA_PORT", "value":kafka_port},
                                        {"name":"KAFKA_TOPIC", "value":kafka_topic}
                                    ],
                                    ports=[
                                        {"container_port": 8080}
                                    ],
                                    volumeMounts=[],
                                    resources=k8s.core.v1.ResourceRequirements(
                                        requests={
                                            "cpu":"1g",
                                            "memory":"1g"
                                        }
                                      )
                           ),
                      ]),
                ),
            ),
        )

        self.consumer_stub = ImageBuilder(
               name="canary_consumer",
               base_image="kdb32",
               files=[
                "consumer.q"
               ],
        )

        self.consumer_deployment = Deployment('kdb_ingest_canary_deployment',
            spec=DeploymentSpecArgs(
                # selector=LabelSelectorArgs(match_labels=labels),
                replicas=1,
                template=PodTemplateSpecArgs(
                    # metadata=ObjectMetaArgs(labels=labels),
                    spec=PodSpecArgs(containers=[
                            k8s.core.v1.ContainerArgs(
                                    name="tickerplant",
                                    image=self.consumer_stub.image.image_name,
                                    env=[
                                        {"name":"KAFKA_HOST", "value":kafka_host},
                                        {"name":"KAFKA_PORT", "value":kafka_port},
                                        {"name":"KAFKA_TOPIC", "value":kafka_topic}
                                    ],
                                    ports=[
                                        {"container_port": 8080}
                                    ],
                                    volumeMounts=[],
                                    resources=k8s.core.v1.ResourceRequirements(
                                        requests={
                                            "cpu":"1g",
                                            "memory":"1g"
                                        }
                                      )
                           ),
                      ]),
                ),
            ),
        )

