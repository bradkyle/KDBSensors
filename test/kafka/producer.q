\l kafka/kfk.q
.utl.require"ws-client"

host:getenv[`KAFKA_HOST]
port:getenv[`KAFKA_PORT]
topic:getenv[`KAFKA_TOPIC]
show (host;port;topic)

kfk_cfg:(!) . flip(
    (`metadata.broker.list;`$":"sv string (host;port));
    (`statistics.interval.ms;`10000);
    (`queue.buffering.max.ms;`1);
    (`fetch.wait.max.ms;`10)
    );
producer:.kfk.Producer[kfk_cfg]

topic:.kfk.Topic[producer;topic;()!()]

.z.ts:{n+:1;.kfk.Pub[topic;.kfk.PARTITION_UA;"BAM";""]}


