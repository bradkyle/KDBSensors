
\c 500 500
\l kafka/kfk.q
\l exporter.q
.utl.require"ws-client"

.sensor.Event:{[sourceid;channelid;agentid;entities;utctime;resp]
    `sid`cid`aid`eid`utc`utcin`resp!();
    }; 

	// Producer logic 
/------------------------------------------------------------------------------------------>``

.sensor.KafkaProducer :{[]
		  
		  
	};

.sensor.KDBProducer :{[]
		  
		  
	};


// Sensor logic 
/------------------------------------------------------------------------------------------>``

.sensor.WebsocketSensor :{[]
		  
		  
	};

.sensor.CronSensor :{[]
		  
		  
	};

.sensor.WebsocketSensor :{[]
		  
		  
	};

// Effector logic 
/------------------------------------------------------------------------------------------>``

