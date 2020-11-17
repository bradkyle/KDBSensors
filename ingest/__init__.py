

class KDBIngress(pulumi.ComponentResource):
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
                           # Engine QUEUE
                           # The queue exposes methods to the services that allow
                           # for events to be inserted into it 
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
                                    env=[],
                                    ports=[],
                                    volumeMounts=[],
                                    resources=k8s.core.v1.ResourceRequirements(
                                        requests={
                                            "cpu":"1g",
                                            "memory":"1g"
                                        }
                                      )
                           ),
                           # Engine TickerPlant
                           # The queue exposes methods to the services that allow
                           # for events to be inserted into it 
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
                                    env=[],
                                    ports=[],
                                    volumeMounts=[],
                                    resources=k8s.core.v1.ResourceRequirements(
                                        requests={
                                            "cpu":"1g",
                                            "memory":"1g"
                                        }
                                      )
                           ),
                           # Market making service
                           # Each engine has a single market maker account with expediated access
                           # to the engine and it's resultant data, it aggregates events revieved from 
                           # the queue and external sources and acts based upon this. 
                           # percepts are pushed to the kafka queue in addition
                           # subscibes to exter
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
                                    env=[],
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

class Router(pulumi.ComponentResource):
    def __init__(self):
        pass

class KDBExchangeEngineRegistry(pulumi.ComponentResource):
    def __init__(self):
        self.instruments = {}

        self.engine_node_pool = gcp.container.NodePool("engine_node",
            cluster=self.k8s_cluster.id,
            project=get_project(),
            initial_node_count=1,
            max_pods_per_node=1,
            node_count=1,
            node_config=gcp.container.NodePoolNodeConfigArgs(
                disk_size_gb=100,
                machine_type="n1-standard-1",
                preemptible=False,
                labels={}
            )
        )

        self.router_image = ()
        self.core_engine_image = ()
        self.engine_queue_image = ()

        self.engine_addresses = {}
        self.engine_deployments = {}
        self.engine_tickerplant_image = ()
        self.market_making_image = ()

        # Routing exposes a single service which in turn 
        # "services" all subsequent requests from the service
        # pods
        username = "username"
        password = "password"
        # qenv_secret = Secret("qenv_secret_"+str(i),
        #     args=SecretArgs(
        #         data={
        #             "username":username,
        #             "password":password
        #         }
        #     ), __opts__=ResourceOptions(provider=self.k8s_provider))
        labels = { 'app': 'router-{0}-{1}'.format(get_project(), get_stack()) }
        router_deployment = k8s.apps.v1.Deployment("router-deployment-"+str(i),
            spec=k8s.apps.v1.DeploymentSpecArgs(
                selector=k8s.meta.v1.LabelSelectorArgs(match_labels=labels),
                replicas=3,
                template=k8s.core.v1.PodTemplateSpecArgs(
                    metadata=k8s.meta.v1.ObjectMetaArgs(labels=labels),
                    spec=k8s.core.v1.PodSpecArgs(containers=[
                          k8s.core.v1.ContainerArgs(
                                name="_".join([str(s) for s in [self.qenv_image.id, self.run_id, i]]),
                                image='nginx',
                                image_pull_policy="IfNotPresent",
                                # livenessProbe=core.v1.Probe(
                                #     exec="",
                                #     failureThreshold=3
                                # ),
                                # redinessProbe=core.v1.Probe(
                                #     exec="",
                                #     failureThreshold=3,
                                # ),
                                # env=[
                                    # core.v1.EnvVar(name="",value=""),
                                    # core.v1.EnvVar(name="",value=""),
                                    # core.v1.EnvVar(name="",value="")
                                # ],
                          ),
                          k8s.core.v1.ContainerArgs(
                            name="_".join([str(s) for s in [self.qenv_image.id, self.run_id, "log_sidecar", i]]),
                            image="nginx",
                            env=[]
                          )
                      ]),
                ),
            ), __opts__=ResourceOptions(provider=self.k8s_provider))

        super().register_outputs({})



    def add_instrument(
          self,
          instrument:InstrumentArgs
      ):
        self.engine_deployments[name] = CoreEngine(

        )
        self.engine_addresses[name] = ()




















