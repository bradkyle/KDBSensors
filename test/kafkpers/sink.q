
\l kafka/kfk.q
\l sym.q

host:getenv[`KAFKA_HOST]
port:getenv[`KAFKA_PORT]
topic:getenv[`KAFKA_TOPIC]
show (host;port;topic)

kfk_cfg:(!) . flip(
    (`metadata.broker.list;`$":"sv string (host;port));
    (`group.id;`0);
    (`fetch.wait.max.ms;`10);
    (`statistics.interval.ms;`10000)
    );
client:.kfk.Consumer[kfk_cfg];


.sink.ingress :{[msg]
    // consume count
    // consume gauge
    // latency time ms
    // todo parse with proto
    .sink.tab[`raw],:msg;
    .sink.tab[x],:enlist msg[`datum]; 

				  
		};


// Subscribe to topic1 and topic2 with different callbacks from a single client
.kfk.Subscribe[client;topic;enlist .kfk.PARTITION_UA;.sink.ingress]


