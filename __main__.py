"""A Google Cloud Python Pulumi program"""

import pulumi
from pulumi_gcp import storage
# from sensors import KDBSensorRegistry
# from monitoring.monitoring import MonitoringCluster
from infra.kafka import StrimziKafkaOperator
from test.sensor import KDBFullSensor
config = pulumi.Config()
# isMinikube = config.get_bool("isMinikube")

kafka = StrimziKafkaOperator(k8s_provider=None)
events_topic = kafka.add_topic("events");

# Sensors 
#--------------------------------------------> 

# AuthSensors and Effectors 
#--------------------------------------------> 

sensor = KDBFullSensor()

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
