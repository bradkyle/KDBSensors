\l kafka/kfk.q

khost:getenv[`KAFKA_HOST]
kport:getenv[`KAFKA_PORT]
ktopic:getenv[`KAFKA_TOPIC]
kgroup:getenv[`KAFKA_GROUP]
show (khost;kport;ktopic)

kfk_cfg:(!) . flip(
    (`metadata.broker.list;(`$":"sv (khost;kport)));
    (`group.id;`0);
    (`fetch.wait.max.ms;`10);
    (`statistics.interval.ms;`10000)
    );
client:.kfk.Consumer[kfk_cfg];

// Subscribe to topic1 and topic2 with different callbacks from a single client
.kfk.Subscribe[client;`$ktopic;enlist .kfk.PARTITION_UA;show]

