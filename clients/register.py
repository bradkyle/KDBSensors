
class KDBSensorRegistry(pulumi.ComponentResource):
    def __init__(self, kafka_ingest, monitoring_cluster, use_ingress_kafka):
        self.sensors = {}
        self.kafka_ingest = kafka_ingest
        self.monitoring_cluster = monitoring_cluster
        self.use_ingress_kafka=use_ingress_kafka

    def add_sensor(self, name, args:KDBSensorArgs):
        pass

