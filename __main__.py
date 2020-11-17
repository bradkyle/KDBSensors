"""A Google Cloud Python Pulumi program"""

import pulumi
from pulumi_gcp import storage
from sensors import KDBSensorRegistry
from monitoring.monitoring import MonitoringCluster

# run initialization

# Create a GCP resource (Storage Bucket)
bucket = storage.Bucket('my-bucket')

# Export the DNS name of the bucket
pulumi.export('bucket_name', bucket.url)

# TODO monitoring cluster

# TODO persist/tickerplant deployment 

sensors.add_sensor("",  args={})
sensors.add_sensor("",  args={})
