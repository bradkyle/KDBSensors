

class KDBIngest(pulumi.ComponentResource):
    """
    Creates the set of deployments neccessary to orchestrate
    persistence on a kubernetes cluster.
    """
    def __init__(
            self,
            instrument,
            monitoring_cluster,
            core_engine_image,
            engine_queue_image,
            engine_tickerplant_image,
            market_making_image
      ):
        labels = { 'app': 'engine-{0}-{1}'.format(get_project(), get_stack()) }
        username = "admin"
        password = "password"
        # ingest_secret = Secret("ingest_secret_"+str(i),
        #     args=SecretArgs(
        #         data={
        #             "username":username,
        #             "password":password
        #         }
        #     ), __opts__=ResourceOptions(provider=self.k8s_provider))

        # TODO add instrument config map

        self.deployment = k8s.apps.v1.StatefulSet("engine-deployment-"+str(i),
            spec=k8s.apps.v1.StatefulSetSpecArgs(
                selector=k8s.meta.v1.LabelSelectorArgs(match_labels=labels),
                service_name="engine_"+str(i),
                replicas=1,
                template=k8s.core.v1.PodTemplateSpecArgs(
                    metadata=k8s.meta.v1.ObjectMetaArgs(labels=labels),
                    spec=k8s.core.v1.PodSpecArgs(
                        containers=[
                            # Engine
                            # Maintains internal state and does matching engine etc
                            # periodically requests from the queue service 
                            k8s.core.v1.ContainerArgs(
                                    name="_".join([str(s) for s in [self.ingest_image.id, self.run_id, i]]),
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

                                    ],
                                    ports=[],
                                    volumeMounts=[],
                                    resources=k8s.core.v1.ResourceRequirements(
                                        requests={
                                            "cpu":"1g",
                                            "memory":"1g"
                                        }
                                      )
                           ),
                        ]
                    )
                ),
            ), __opts__=ResourceOptions(provider=self.k8s_provider))

            self.monitoring_cluster.add_service_monitor(
                name="ingest",
                labels=labels,
                namespace="default",
                interval="10s",
                provider=self.k8s_provider
            )

            self.monitoring_cluster.add_grafana_dashboard()


