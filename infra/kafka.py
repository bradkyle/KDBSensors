import pulumi_docker as docker
import pulumi_gcp as gcp
import pulumi_kubernetes as k8s

class StrimziKafkaOperator(pulumi.ComponentResource):
    def __init__(self, k8s_provider):
        self.k8s_provider = k8s_provider
        self.chart = k8s.helm.v3.Chart(
            "strimzi",
            k8s.helm.v3.ChartOpts( # TODO add bitnami/grafana
                chart="strimzi-kafka-operator",
                # version="3.4.7",
                fetch_opts=FetchOpts(
                    repo="https://strimzi.io/charts/",
                ),
            ),
        )
            # opts=ResourceOptions(provider=self.k8s_provider))

