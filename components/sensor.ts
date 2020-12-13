
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

// Arguments for the demo app.
export interface SensorPipelineArgs {
    provider: k8s.Provider; // Provider resource for the target Kubernetes cluster.
    kafka:kafka.KafkaOperator,
    topicName?:string;
    pullPolicy?:string
    sensor: SensorArgs;
    persist: PersistArgs;
}

export class Sensor extends pulumi.ComponentResource {
    public readonly bucket: gcp.storage.Bucket; 
    public readonly persistImage: docker.Image; 
    public readonly sensorImage: docker.Image; 
    public readonly sensor: k8s.apps.v1.Deployment;
    public readonly persist: k8s.apps.v1.Deployment;

    constructor(name: string,
                args: SensorPipelineArgs,
                opts: pulumi.ComponentResourceOptions = {}) {
        super("beast:sensor:sensor", name, args, opts);

        const kafkaTopic = args.kafka.addTopic((args.topicName || `${name}-topic`),{}); 

        // MULTI_REGIONAL, REGIONAL, NEARLINE, COLDLINE, ARCHIVE.
        //The bucket into which data should be persisted 
        this.bucket = new gcp.storage.Bucket(`${name}-bucket`,{
            name:`${name}-bucket`,
            location: "US",
            storageClass: "REGIONAL",
            uniformBucketLevelAccess: true,
            versioning:{
                  enabled:false,
            },
            logging: {
                logBucket:"",
            }, 
            lifecycleRules:[
                {
                    action: {type: "SetStorageClass", storageClass: "Archive"},
                    condition: {
                        age: 7,
                        matchesStorageClasses: ["Coldline", "Nearline", "Standard"],
                    }
                },
            ],
        });

        // Create a Secret to hold the MariaDB credentials.
        const kdbSecret = new k8s.core.v1.Secret("kdb", {
            stringData: {
                "kdb-password": new random.RandomPassword("mariadb-pw", {length: 12}).result
            }
        }, { provider: args.provider });

        this.sensorImage = new docker.Image(`${name}-sensor-image`, {
            imageName: (args.sensor.imageName || "thorad/sensor"),
            build: {
                dockerfile: args.sensor.dockerfile,
                context: args.sensor.dockercontext,
            },
            skipPush: false,
        });

        // Create the kuard Deployment.
        const sensorLabels = {app: "sensor"}; // TODO change to statefulset
        this.sensor = new k8s.apps.v1.Deployment(`${name}-sensor`, {
            spec: {
                selector: {matchLabels: sensorLabels},
                replicas: 1,
                template: {
                    metadata: {labels: sensorLabels},
                    spec: {
                        containers: [
                            {
                                name:`${name}-sensor`, 
                                image: this.persistImage.imageName,
                                ports: [{containerPort: 8080, name: "kdb"}],
                                livenessProbe: {
                                    httpGet: {path: "/healthy", port: "kdb"},
                                    initialDelaySeconds: 5,
                                    timeoutSeconds: 1,
                                    periodSeconds: 10,
                                    failureThreshold: 3,
                                },
                                readinessProbe: {
                                    httpGet: {path: "/ready", port: "kdb"},
                                    initialDelaySeconds: 5,
                                    timeoutSeconds: 1,
                                    periodSeconds: 10,
                                    failureThreshold: 3,
                                },
                            },
                        ],
                    },
                },
            },
        }, {provider: args.provider, parent: this});

        // TODO a secodary container that services requests

        // args.monitoring.addMonitor();
        this.persistImage = new docker.Image(`${name}-persist-image`, {
            imageName: (args.sensor.imageName || "thorad/persist"),
            build: {
                dockerfile: args.sensor.dockerfile,
                context: args.sensor.dockercontext,
            },
            skipPush: false,
        });

        // for (i of)
        const appLabels = {app: "ingest"};
        this.datapaths = (args.datapaths || []);

        // const gcloudKey = new k8s.core.v1.ConfigMap(`${name}-gcloud-key`, {
        //     metadata: { labels: appLabels },
        //     data: { "data.list": JSON.stringify(this.datapaths)},
        // });
        // const gcloudKeyName = gcloudKey.metadata.apply(m => m.name);

        // gsutil -m cp -r data.list
        const ingestConfig = new k8s.core.v1.ConfigMap(`${name}-ingest`, {
            metadata: { labels: appLabels },
            data: { "data.list": this.datapaths.join("\n")},
        }, {provider: args.provider, parent: this});
        const ingestConfigName = ingestConfig.metadata.apply(m => m.name);


        const datapath = (args.dataMountPath || "/ingest/data");
        this.deployment = new k8s.apps.v1.StatefulSet(`${name}-ingest`, {
            spec: {
                selector: {
                    matchLabels: appLabels,
                },
                serviceName: "ingest",
                updateStrategy :{
                    // type: "RollingUpdate"
                },
                replicas: 1,
                template: {
                    metadata: {labels: appLabels},
                    spec: {
                        serviceAccountName: "default",
                        containers: [
                            {
                                name: "ingest",
                                image: this.image.imageName,
                                imagePullPolicy:(args.pullPolicy || "Always"), 
                                env: [
                                    { 
                                        name: "GOOGLE_APPLICATION_CREDENTIALS", 
                                        value: this.keyfilepath 
                                    },
                                    { 
                                        name: "CONFIG_PATH", 
                                        value: this.keyfilepath 
                                    },
                                    { 
                                        name: "DATA_PATH", 
                                        value: "/ingest/testdata/events" 
                                    }
                                ],
                                volumeMounts: [
                                    {
                                        name: "data-list",
                                        mountPath: "/ingest/config/datalist"
                                    },
                                    {
                                        name:"data",
                                        mountPath:datapath
                                    }
                                ],
                                ports: [
                                      {containerPort: 5000, name: "kdb"}
                                ],
                                lifecycle:{
                                    postStart :{
                                        exec : {
                                            command: [
                                                "/bin/sh",
                                                "./poststart.sh", 
                                                datapath
                                            ]
                                        }
                                    },
                                    preStop:{
                                        exec : {
                                            command: [
                                                "/bin/sh",
                                                "./prestop.sh", 
                                                datapath
                                            ]
                                        }
                                    }
                                }

                            },
                        ],
                        volumes :[
                            // {
                            //     name: "google-cloud-key",
                            //     secret : {}
                            // },
                        ],
                    },
                },
                volumeClaimTemplates: [
                    {
                        metadata: {
                            name: "data",
                            labels: {
                                app: "ingest",
                                component: "master",
                                release: "example",
                            }
                        },
                        spec: {
                            accessModes: [
                                "ReadWriteOnce"
                            ],
                            resources: {
                                requests: {
                                    storage: "5Gi"
                                }
                            }
                        }
                    }
                ]
            },
        }, {provider: args.provider, parent: this});
        this.registerOutputs();
    }
}
