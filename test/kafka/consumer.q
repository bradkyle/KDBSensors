\l kafka/kfk.q
.utl.require"ws-client"

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

// Subscribe to topic1 and topic2 with different callbacks from a single client
.kfk.Subscribe[client;topic;enlist .kfk.PARTITION_UA;show]

