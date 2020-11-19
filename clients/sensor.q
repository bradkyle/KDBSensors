
\c 500 500
\l kafka/kfk.q
\l exporter.q
.utl.require"ws-client"

.sensor.Event:{[sourceid;channelid;agentid;entities;utctime;resp]
    `sid`cid`aid`eid`utc`utcin`resp!();
    }; 

.sensor.Channel:{[]
		  
		  }

.sensor.sensor :{

				};

.sensor.wss.init :{[host;port;topic;url;channels;parser]
			kfk_cfg:(!) . flip(
				(`metadata.broker.list;`$":"sv string (khost;kport));
				(`statistics.interval.ms;`10000);
				(`queue.buffering.max.ms;`1);
				(`fetch.wait.max.ms;`10)
				);

			producer:.kfk.Producer[kfk_cfg];
			topic:.kfk.Topic[producer;topic;()!()];

			upd:{
				.prom.updval[`num_events;+;1];
				e:.sensor.Event[x];
				.kfk.Pub[.bitmex.topic;.kfk.PARTITION_UA;x;""];
			 };

		  sub:{

			 };

		 .ws.open[url;sub]; 
		};

.sensor.authwss.init :{
		.sensor.wss[]
		};

.sensor.cron.init :{

		};

.sensor.authcron.init :{

		};


.sensor.handlers:();


.sensor.run[];
