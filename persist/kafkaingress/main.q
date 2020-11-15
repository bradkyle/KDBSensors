\l prometheus/q/exporter.q
\l kafka/kfk.q

\d .prom

// h:hopen 8080;
// h"N:100000"
// h".prom.tab:([]N?1f;N?10;N?0b;N?`2;N?0p)"
// md:0;

// split a minute into appropriately sized random time bins
// tsplit:0 20 35 45 55_neg[count t]?t:til 60;
// .z.ts:{
//   // current second of a minute
//   min_val:`ss$.z.t;
//   $[min_val in tsplit 0;
//     // upsert values into .prom.tab on the server
//     h"N:50000+rand 100000;`.prom.tab upsert([]N?1f;N?10;N?0b;N?`3;N?0p)";
//     // remove a random number of rows from .prom.tab
//     min_val in tsplit 1;
//     neg[h]"delete from `.prom.tab where i<10000+rand 100000";
//     // run either a HTTP request or sync select statement
//     min_val in tsplit 2;
//     $[0~md mod 2;(.Q.hg["http://localhost:8080/?1+1"];);h"select first x from .prom.tab"]
//     // Cause either a sync or async error
//     min_val in tsplit 3;
//     $[0~md mod 3;(h"1+`a");(neg[h]"1+`a")];
//     // Run an async select statement
//     neg[h]"select first x from .prom.tab"];
//   // run garbage collection on the server and local process every 30s
//   if[0~first md mod 30;h".Q.gc[]";.Q.gc[]];
//   if[5000000 < h"count .prom.tab";
//      neg[h]"delete from `.prom.tab where i< 4000000";
//      h".Q.gc[]";.Q.gc[]];
//   md+:1;
//   }
// -1".z.ts set to execute every second";
// system"t 1000"

/* h:hopen":5000"; */
/* h("logStarted";0); */
// https://github.com/edenhill/librdkafka/wiki/How-to-decrease-message-latency
args:.Q.opt[.z.x];
args[`brokers]:first `$args[`brokers];
args[`topic]:first `$args[`topic];
  
kfk_cfg:(!) . flip(
    (`metadata.broker.list;args[`brokers]);
    (`group.id;`0);
    (`fetch.wait.max.ms;`10);
    (`statistics.interval.ms;`10000)
    );
client:.kfk.Consumer[kfk_cfg];

// Topics to subscribe to
data2:();
ingress:{[msg]

  msg[`data]:"c"$msg[`data];
  msg[`rcvtime]:.z.t;
  data2,::enlist msg;

  };

// Subscribe to topic1 and topic2 with different callbacks from a single client
.kfk.Subscribe[client;args[`topic];enlist .kfk.PARTITION_UA;ingress]

client_meta:.kfk.Metadata[client];
show client_meta`topics;
