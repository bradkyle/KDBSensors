"""A Google Cloud Python Pulumi program"""

import pulumi
from pulumi_gcp import storage
# from sensors import KDBSensorRegistry
# from monitoring.monitoring import MonitoringCluster
from infra.kafka import StrimziKafkaOperator
# from test.sensor import KDBFullSensor
from test.kafka import PYIngestCanary
config = pulumi.Config()
# isMinikube = config.get_bool("isMinikube")

# Monitoring
#=========================================================================================> 

kafka_operator = StrimziKafkaOperator(k8s_provider=None)

canary = PYIngestCanary(name="canary",kafka_operator=kafka_operator)

# Binance Futures 
# beast.client.make()
# beast.client.make()

# ingest = KDBIngestWorker(
#     topic=kafka.get_topic("events"),
#     output=(),
#     compression=True,
# )

# core.make(
#     ingest=ingest,
#     sensors={
#        "":"",
#        "":"",
#     },
#     agent=CoreInferenceWorker(
#         state=CoreStateManager(),
#         model=CoreModelWorker()
#     ),
#     effectors={},
#     percept_store=KDBPerceptStore(
#
#     )
# )
