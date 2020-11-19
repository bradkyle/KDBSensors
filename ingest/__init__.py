
import pulumi
import pulumi_docker as docker
import pulumi_gcp as gcp
import pulumi_kubernetes as k8s

class KDBIngestCanary(pulumi.ComponentResource):
    """
    Creates a simple KDB instance to check that kafka reading etc
    is working correctly with kdb
    """
    def __init__(self, kafka_host, kafka_port, kafka_topic):
        self.image = docker.Image()

        self.deployment = Deployment('kdb_ingest_canary',
            spec=DeploymentSpecArgs(
                # selector=LabelSelectorArgs(match_labels=labels),
                replicas=1,
                template=PodTemplateSpecArgs(
                    # metadata=ObjectMetaArgs(labels=labels),
                    spec=PodSpecArgs(containers=[
                            k8s.core.v1.ContainerArgs(
                                    name="tickerplant",
                                    image='nginx',
                                    image_pull_policy="IfNotPresent",
                                    liveness_probe=core.v1.Probe(
                                        exec="",
                                        failureThreshold=3
                                    ),
                                    redinessProbe=core.v1.Probe(
                                        exec="",
                                        failureThreshold=3,
                                    ),
                                    env=[
                                        {"name":"KAFKA_HOST", "value":""},
                                        {"name":"KAFKA_PORT", "value":""},
                                        {"name":"KAFKA_TOPIC", "value":""}
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



# class KDBIngest(pulumi.ComponentResource):
#     """
#     Creates the set of deployments neccessary to orchestrate
#     persistence on a kubernetes cluster.
#     """
#     def __init__(
#             self,
#             instrument,
#             monitoring_cluster,
#             core_engine_image,
#             engine_queue_image,
#             engine_tickerplant_image,
#             market_making_image
#       ):
#         labels = { 'app': 'engine-{0}-{1}'.format(get_project(), get_stack()) }
#         username = "admin"
#         password = "password"
#         # ingest_secret = Secret("ingest_secret_"+str(i),
#         #     args=SecretArgs(
#         #         data={
#         #             "username":username,
#         #             "password":password
#         #         }
#         #     ), __opts__=ResourceOptions(provider=self.k8s_provider))

#         # TODO add instrument config map

#         self.deployment = k8s.apps.v1.StatefulSet("engine-deployment-"+str(i),
#             spec=k8s.apps.v1.StatefulSetSpecArgs(
#                 selector=k8s.meta.v1.LabelSelectorArgs(match_labels=labels),
#                 service_name="engine_"+str(i),
#                 replicas=1,
#                 template=k8s.core.v1.PodTemplateSpecArgs(
#                     metadata=k8s.meta.v1.ObjectMetaArgs(labels=labels),
#                     spec=k8s.core.v1.PodSpecArgs(
#                         containers=[
#                             # Tickerplant 
#                             # Reads from a given kafka topic and sends the events to the 
#                             # respective subscribers and persisters
#                             k8s.core.v1.ContainerArgs(
#                                     name="tickerplant",
#                                     image='nginx',
#                                     image_pull_policy="IfNotPresent",
#                                     liveness_probe=core.v1.Probe(
#                                         exec="",
#                                         failureThreshold=3
#                                     ),
#                                     redinessProbe=core.v1.Probe(
#                                         exec="",
#                                         failureThreshold=3,
#                                     ),
#                                     env=[

#                                     ],
#                                     ports=[],
#                                     volumeMounts=[],
#                                     resources=k8s.core.v1.ResourceRequirements(
#                                         requests={
#                                             "cpu":"1g",
#                                             "memory":"1g"
#                                         }
#                                       )
#                            ),
#                            # KDB container that serves to persist the events
#                            # in a partitioned manner to disk
#                            k8s.core.v1.ContainerArgs(
#                                     name="persist",
#                                     image='nginx',
#                                     image_pull_policy="IfNotPresent",
#                                     liveness_probe=core.v1.Probe(
#                                         exec="",
#                                         failureThreshold=3
#                                     ),
#                                     redinessProbe=core.v1.Probe(
#                                         exec="",
#                                         failureThreshold=3,
#                                     ),
#                                     env=[

#                                     ],
#                                     ports=[],
#                                     volumeMounts=[],
#                                     resources=k8s.core.v1.ResourceRequirements(
#                                         requests={
#                                             "cpu":"1g",
#                                             "memory":"1g"
#                                         }
#                                       )
#                            ),
#                            # Python updloader container that periodically replicates
#                            # the hdb to cloud storage and removes old data.
#                            k8s.core.v1.ContainerArgs(
#                                     name="persist",
#                                     image='nginx',
#                                     image_pull_policy="IfNotPresent",
#                                     liveness_probe=core.v1.Probe(
#                                         exec="",
#                                         failureThreshold=3
#                                     ),
#                                     redinessProbe=core.v1.Probe(
#                                         exec="",
#                                         failureThreshold=3,
#                                     ),
#                                     env=[

#                                     ],
#                                     ports=[],
#                                     volumeMounts=[],
#                                     resources=k8s.core.v1.ResourceRequirements(
#                                         requests={
#                                             "cpu":"1g",
#                                             "memory":"1g"
#                                         }
#                                       )
#                            ),
#                            # KDB container that serves/ broadcasts the incoming events
#                            # to the subscribers in the pod
#                            k8s.core.v1.ContainerArgs(
#                                     name="broadcaster",
#                                     image='nginx',
#                                     image_pull_policy="IfNotPresent",
#                                     liveness_probe=core.v1.Probe(
#                                         exec="",
#                                         failureThreshold=3
#                                     ),
#                                     redinessProbe=core.v1.Probe(
#                                         exec="",
#                                         failureThreshold=3,
#                                     ),
#                                     env=[

#                                     ],
#                                     ports=[],
#                                     volumeMounts=[],
#                                     resources=k8s.core.v1.ResourceRequirements(
#                                         requests={
#                                             "cpu":"1g",
#                                             "memory":"1g"
#                                         }
#                                       )
#                            ),
#                         ]
#                     )
#                 ),
#             ), __opts__=ResourceOptions(provider=self.k8s_provider))

#             self.monitoring_cluster.add_service_monitor(
#                 name="ingest",
#                 labels=labels,
#                 namespace="default",
#                 interval="10s",
#                 provider=self.k8s_provider
#             )

#             self.monitoring_cluster.add_grafana_dashboard()


