// Contains logic for reading data from the given kafka topic and sending it off
// to the respective workers
\l ../kfk.q

kfk_cfg:(!) . flip(
    (`metadata.broker.list;`:9092);
    (`group.id;`0);
    (`fetch.wait.max.ms;`10);
    (`statistics.interval.ms;`10000)
    );
client:.kfk.Consumer[kfk_cfg];

upd :{
    // parse in proto 
    // send
      
    };

// Subscribe to topic1 and topic2 with different callbacks from a single client
.kfk.Subscribe[client;topic;enlist .kfk.PARTITION_UA;upd]

client_meta:.kfk.Metadata[client];
show client_meta`topics;
