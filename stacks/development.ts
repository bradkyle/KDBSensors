
import * as k8s from "@pulumi/kubernetes";
import * as pulumi from "@pulumi/pulumi";
import * as local from "../components/lclcluster"

export interface DevConfig {

}

export function setup(config:DevConfig) {
        let mon = new monitoring.Monitoring();
        let kfk = new kafka.KafkaOperator();  

        let sensors Record<string, Sensor> = {}

        sensors["binance"] = new sensor.Sensor("binance";{
            gcsMountPath:"",
            provider:local.provider,


        });
        
};
