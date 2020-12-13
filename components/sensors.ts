

import * as k8s from "@pulumi/kubernetes";
import * as pulumi from "@pulumi/pulumi";
import * as random from "@pulumi/random";
import * as kafka from "./kafka"
import * as gcp from "@pulumi/gcp";
import * as docker from "@pulumi/docker";
// import * as dkr from "./docker"

export enum StorageProvider {
    LCL,
    GCS,
    AWS,
}

export interface PersistArgs {
    imageName?:string;
    dockerfile?:string;
    dockercontext?:string;
    dataMountPath:string;
    storageProvider?:StorageProvider
}

export interface SensorArgs {
    imageName?:string;
    dockerfile?:string;
    dockercontext?:string;
}


export class Sensor extends pulumi.ComponentResource {

    constructor(name: string,
                args: SensorPipelineArgs,
                opts: pulumi.ComponentResourceOptions = {}) {
        super("beast:sensor:sensor", name, args, opts);

    }
}
