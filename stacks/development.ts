
import * as k8s from "@pulumi/kubernetes";
import * as pulumi from "@pulumi/pulumi";
import * as local from "../components/cluster/lcl"
import * as monit from "../components/monitoring"
import * as kafka from "../components/kafka"
import * as sensor from "../components/sensor"

export interface DevConfig {

}

export function setup(config:DevConfig) {
        let mon = new monit.Monitoring();
        let kfk = new kafka.Kafka("kafka",{
            provider:local.provider,
        });  

        let sensors Record<string, sensor.Sensor> = {}

        sensors["binance"] = new sensor.Sensor("binance",{
            provider:local.provider,
            kafka:kfk,
            topicName:"binance",
            sensor:{

            },
            persist:{
                gcsPath:""
            }
        });
        
};
