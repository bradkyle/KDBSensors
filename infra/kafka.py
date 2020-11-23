import pulumi
import pulumi_docker as docker
import pulumi_gcp as gcp
import pulumi_kubernetes as k8s

class KafkaTopic(pulumi.ComponentResource):
    def __init__(
        self,
        name,
        replicas=1,
        partitions=10,
        retention_ms=86400000,
        segment_bytes=1073741824,
        retention_bytes=5000000000
      ):
        self.name = name
        self.partitions = partitions
        self.replicas = replicas
        self.retention_ms=retention_ms
        self.segment_bytes = segment_bytes
        self.retention_bytes = retention_bytes
        self.topic = k8s.apiextensions.CustomResource(
            "kafka",
             api_version="kafka.strimzi.io/v1beta1",
             kind="KafkaTopic",
             metadata={
                "name": self.name,
                "namespace": "default",
                "labels": {
                  "strimzi.io/cluster": "strimzi-cluster"
                }
             },
             spec={
                "partitions": self.partitions,
                "replicas": self.replicas,
                "config": {
                  "retention.ms": self.retention_ms,
                  "segment.bytes": self.segment_bytes,
                    "retention.bytes": self.retention_bytes
                }
            })

# TODO storage configuration
# TODO replica configuration

class StrimziKafkaOperator(pulumi.ComponentResource):
    def __init__(self, k8s_provider):
        self.k8s_provider = k8s_provider
        self.topics = {}

        self.host="strimzi-cluster-kafka-bootstrap"
        self.port=9092

        self.chart = k8s.helm.v3.Chart(
            "strimzi",
            k8s.helm.v3.ChartOpts( # TODO add bitnami/grafana
                chart="strimzi-kafka-operator",
                # version="3.4.7",
                fetch_opts=k8s.helm.v3.FetchOpts(
                    repo="https://strimzi.io/charts/",
                ),
            ),
        )
        # opts=ResourceOptions(provider=self.k8s_provider))
        # opts=pulumi.ResourceOptions(depends_on=[crd]))

        self.kafka = k8s.apiextensions.CustomResource(
            "kafka",
             api_version="kafka.strimzi.io/v1beta1",
             kind="Kafka",
             metadata={
                "name":"strimzi-cluster"
             },
             spec={
                "kafka": {
                  "version": "2.4.0",
                  "replicas": 3,
                  "listeners": {
                    "plain": {},
                    "tls": {}
                  },
                  "readinessProbe": {
                    "initialDelaySeconds": 15,
                    "timeoutSeconds": 5
                  },
                  "livenessProbe": {
                    "initialDelaySeconds": 15,
                    "timeoutSeconds": 5
                  },
                  "config": {
                    "offsets.topic.replication.factor": 3,
                    "transaction.state.log.replication.factor": 3,
                    "transaction.state.log.min.isr": 2,
                    "log.message.format.version": "2.4"
                  },
                  "storage": {
                    "type": "jbod",
                    "volumes": [
                      {
                        "id": 0,
                        "type": "persistent-claim",
                        "size": "100Gi",
                          "deleteClaim": False
                      }
                    ]
                  },
                  "metrics": {
                    "lowercaseOutputName": True,
                    "rules": [
                      {
                        "pattern": "kafka.server<type=(.+), name=(.+), clientId=(.+), topic=(.+), partition=(.*)><>Value",
                        "name": "kafka_server_$1_$2",
                        "type": "GAUGE",
                        "labels": {
                          "clientId": "$3",
                          "topic": "$4",
                          "partition": "$5"
                        }
                      },
                      {
                        "pattern": "kafka.server<type=(.+), name=(.+), clientId=(.+), brokerHost=(.+), brokerPort=(.+)><>Value",
                        "name": "kafka_server_$1_$2",
                        "type": "GAUGE",
                        "labels": {
                          "clientId": "$3",
                          "broker": "$4:$5"
                        }
                      },
                      {
                        "pattern": "kafka.(\\w+)<type=(.+), name=(.+)Percent\\w*><>MeanRate",
                        "name": "kafka_$1_$2_$3_percent",
                        "type": "GAUGE"
                      },
                      {
                        "pattern": "kafka.(\\w+)<type=(.+), name=(.+)Percent\\w*><>Value",
                        "name": "kafka_$1_$2_$3_percent",
                        "type": "GAUGE"
                      },
                      {
                        "pattern": "kafka.(\\w+)<type=(.+), name=(.+)Percent\\w*, (.+)=(.+)><>Value",
                        "name": "kafka_$1_$2_$3_percent",
                        "type": "GAUGE",
                        "labels": {
                          "$4": "$5"
                        }
                      },
                      {
                        "pattern": "kafka.(\\w+)<type=(.+), name=(.+)PerSec\\w*, (.+)=(.+), (.+)=(.+)><>Count",
                        "name": "kafka_$1_$2_$3_total",
                        "type": "COUNTER",
                        "labels": {
                          "$4": "$5",
                          "$6": "$7"
                        }
                      },
                      {
                        "pattern": "kafka.(\\w+)<type=(.+), name=(.+)PerSec\\w*, (.+)=(.+)><>Count",
                        "name": "kafka_$1_$2_$3_total",
                        "type": "COUNTER",
                        "labels": {
                          "$4": "$5"
                        }
                      },
                      {
                        "pattern": "kafka.(\\w+)<type=(.+), name=(.+)PerSec\\w*><>Count",
                        "name": "kafka_$1_$2_$3_total",
                        "type": "COUNTER"
                      },
                      {
                        "pattern": "kafka.(\\w+)<type=(.+), name=(.+), (.+)=(.+), (.+)=(.+)><>Value",
                        "name": "kafka_$1_$2_$3",
                        "type": "GAUGE",
                        "labels": {
                          "$4": "$5",
                          "$6": "$7"
                        }
                      },
                      {
                        "pattern": "kafka.(\\w+)<type=(.+), name=(.+), (.+)=(.+)><>Value",
                        "name": "kafka_$1_$2_$3",
                        "type": "GAUGE",
                        "labels": {
                          "$4": "$5"
                        }
                      },
                      {
                        "pattern": "kafka.(\\w+)<type=(.+), name=(.+)><>Value",
                        "name": "kafka_$1_$2_$3",
                        "type": "GAUGE"
                      },
                      {
                        "pattern": "kafka.(\\w+)<type=(.+), name=(.+), (.+)=(.+), (.+)=(.+)><>Count",
                        "name": "kafka_$1_$2_$3_count",
                        "type": "COUNTER",
                        "labels": {
                          "$4": "$5",
                          "$6": "$7"
                        }
                      },
                      {
                        "pattern": "kafka.(\\w+)<type=(.+), name=(.+), (.+)=(.*), (.+)=(.+)><>(\\d+)thPercentile",
                        "name": "kafka_$1_$2_$3",
                        "type": "GAUGE",
                        "labels": {
                          "$4": "$5",
                          "$6": "$7",
                          "quantile": "0.$8"
                        }
                      },
                      {
                        "pattern": "kafka.(\\w+)<type=(.+), name=(.+), (.+)=(.+)><>Count",
                        "name": "kafka_$1_$2_$3_count",
                        "type": "COUNTER",
                        "labels": {
                          "$4": "$5"
                        }
                      },
                      {
                        "pattern": "kafka.(\\w+)<type=(.+), name=(.+), (.+)=(.*)><>(\\d+)thPercentile",
                        "name": "kafka_$1_$2_$3",
                        "type": "GAUGE",
                        "labels": {
                          "$4": "$5",
                          "quantile": "0.$6"
                        }
                      },
                      {
                        "pattern": "kafka.(\\w+)<type=(.+), name=(.+)><>Count",
                        "name": "kafka_$1_$2_$3_count",
                        "type": "COUNTER"
                      },
                      {
                        "pattern": "kafka.(\\w+)<type=(.+), name=(.+)><>(\\d+)thPercentile",
                        "name": "kafka_$1_$2_$3",
                        "type": "GAUGE",
                        "labels": {
                          "quantile": "0.$4"
                        }
                      }
                    ]
                  }
                },
                "zookeeper": {
                  "replicas": 3,
                  "readinessProbe": {
                    "initialDelaySeconds": 15,
                    "timeoutSeconds": 5
                  },
                  "livenessProbe": {
                    "initialDelaySeconds": 15,
                    "timeoutSeconds": 5
                  },
                  "storage": {
                    "type": "persistent-claim",
                    "size": "5Gi",
                    "deleteClaim": False
                  },
                  "metrics": {
                    "lowercaseOutputName": True,
                    "rules": [
                      {
                        "pattern": "org.apache.ZooKeeperService<name0=ReplicatedServer_id(\\d+)><>(\\w+)",
                        "name": "zookeeper_$2",
                        "type": "GAUGE"
                      },
                      {
                        "pattern": "org.apache.ZooKeeperService<name0=ReplicatedServer_id(\\d+), name1=replica.(\\d+)><>(\\w+)",
                        "name": "zookeeper_$3",
                        "type": "GAUGE",
                        "labels": {
                          "replicaId": "$2"
                        }
                      },
                      {
                        "pattern": "org.apache.ZooKeeperService<name0=ReplicatedServer_id(\\d+), name1=replica.(\\d+), name2=(\\w+)><>(Packets.*)",
                        "name": "zookeeper_$4",
                        "type": "COUNTER",
                        "labels": {
                          "replicaId": "$2",
                          "memberType": "$3"
                        }
                      },
                      {
                        "pattern": "org.apache.ZooKeeperService<name0=ReplicatedServer_id(\\d+), name1=replica.(\\d+), name2=(\\w+)><>(\\w+)",
                        "name": "zookeeper_$4",
                        "type": "GAUGE",
                        "labels": {
                          "replicaId": "$2",
                          "memberType": "$3"
                        }
                      },
                      {
                        "pattern": "org.apache.ZooKeeperService<name0=ReplicatedServer_id(\\d+), name1=replica.(\\d+), name2=(\\w+), name3=(\\w+)><>(\\w+)",
                        "name": "zookeeper_$4_$5",
                        "type": "GAUGE",
                        "labels": {
                          "replicaId": "$2",
                          "memberType": "$3"
                        }
                      },
                      {
                        "pattern": "org.apache.ZooKeeperService<name0=StandaloneServer_port(\\d+)><>(\\w+)",
                        "type": "GAUGE",
                        "name": "zookeeper_$2"
                      },
                      {
                        "pattern": "org.apache.ZooKeeperService<name0=StandaloneServer_port(\\d+), name1=InMemoryDataTree><>(\\w+)",
                        "type": "GAUGE",
                        "name": "zookeeper_$2"
                      }
                    ]
                  }
                },
                "entityOperator": {
                  "topicOperator": {},
                  "userOperator": {}
                },
                "kafkaExporter": {
                  "topicRegex": ".*",
                  "groupRegex": ".*"
                }
            })


    def add_topic(self,
                  name,
                  replicas=1,
                  partitions=10,
                  retention_ms=86400000,
                  segment_bytes=1073741824,
                  retention_bytes=5000000000
        ):
        topic = KafkaTopic(
            name=name,
            replicas=replicas,
            partitions=partitions,
            retention_bytes=retention_bytes,
            retention_ms=retention_ms,
            segment_bytes=segment_bytes
        )
        self.topics[topic] = topic
        return topic











