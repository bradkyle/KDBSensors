import pulumi
from pulumi_docker import Image, DockerBuild

# https://github.com/weaveworks/grafanalib
# Used for building grafana dashboards dynamically
from grafanalib.core import (
    Alert, AlertCondition, Dashboard, Graph,
    GreaterThan, OP_AND, OPS_FORMAT, Row, RTYPE_SUM, SECONDS_FORMAT,
    SHORT_FORMAT, single_y_axis, Target, TimeRange, YAxes, YAxis
)

class KDBSensorArgs:
    """
    The arguments necessary to create the KDB sensor
    """
    def __init__(self,
                 description,
                 sensor_path):
        """
        Constructs KDBSensorArgs
        :param description: A human readable description of the sensor
        """
        self.description=description
        self.build_context = build_context
        self.kafka_host = kafka_host
        self.kafka_port = kafka_port
        self.kafka_user = kafka_user
        self.kafka_pass = kafka_pass

#TODO security config for kdb
#TODO if uses kafka sensor pass kafka details into container
class KDBSensor(pulumi.ComponentResource):
      """
      Creates a performant kdb sensor with configurable persistence, logging and security that can
      be (should be) deployed on a kubernetes cluster
      - DHCP options for the given private hosted zone name
      - An Internet gateway
      - Subnets of appropriate sizes for public and private subnets, for each availability zone specified
      - A route table routing traffic from public subnets to the internet gateway
      - NAT gateways (and accoutrements) for each private subnet, and appropriate routing
      - Optionally, S3 and DynamoDB endpoints
      """

      def __init__(self,
                   name:str,
                   args:KDBSensorArgs,
                   ):
        """
        Constructs a Vpc.
        :param name: The Pulumi resource name. Child resource names are constructed based on this.
        :param args: A VpcArgs object containing the arguments for VPC constructin.
        :param opts: A pulumi.ResourceOptions object.
        """
        super().__init__('KDBSensor', name, None, opts)

        # Make base info available to other methods
        self.name = name
        self.description = args.description
        self.base_tags = args.base_tags

        #TODO if uses kafka configure to use
        self.dockerfile = DockerFileBuilder(
            base_image=None,
            files=[]
            command="q -p {port} "
        )

        #TODO move in entrypoint and docker file
        self.image = Image(
            "sensor-image",
            image_name="",
            build=DockerBuild(
                target="dependencies",
                context=self.dockerfile.path,
            ),
            skip_push=True,
        ) # TODO skp

        self.deployment = k8s.apps.v1.Deployment("sensor-deployment-"+str(name),
            spec=k8s.apps.v1.DeploymentSpecArgs(
                selector=k8s.meta.v1.LabelSelectorArgs(match_labels=labels),
                replicas=1,
                template=k8s.core.v1.PodTemplateSpecArgs(
                    metadata=k8s.meta.v1.ObjectMetaArgs(labels=labels),
                    spec=k8s.core.v1.PodSpecArgs(containers=[
                          k8s.core.v1.ContainerArgs(
                                name="_".join([str(s) for s in [self.qenv_image.id, self.run_id, i]]),
                                image='kdb',
                                image_pull_policy="IfNotPresent",
                                # livenessProbe=core.v1.Probe(
                                #     exec="",
                                #     failureThreshold=3
                                # ),
                                # redinessProbe=core.v1.Probe(
                                #     exec="",
                                #     failureThreshold=3,
                                # ),
                                env=[
                                    {"name":"SENSOR_NAME", "value":""},
                                    {"name":"KAFKA_HOST", "value":""},
                                    {"name":"KAFKA_PORT", "value":""},
                                    {"name":"KAFKA_TOPIC", "value":""}
                                ],
                                ports=[
                                    {"container_port": 8080}
                                ],
                          )
                      ]),
                ),
            ), __opts__=ResourceOptions(provider=self.k8s_provider))





