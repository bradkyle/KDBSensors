
sensor_cfg:(!) . flip(
    (`metadata.broker.list;`kafka1:9092);
    (`url;`kafka1:9092);
    (`group.id;`0);
    (`fetch.wait.max.ms;`10);
    (`statistics.interval.ms;`10000)
    );
sensor:.sensor.WssSensor[sensor_cfg];


.sensor.msg.snapshot:{
  /* handle snapshot messages */
  x:"SSFF"$x;                                                                       //cast dictionary to relevant types
  s:.Q.id x`product_id;                                                             //extract sym, remove bad chars
  askst[s]:stdepth sublist (!/) flip x`asks;                                        //get ask state
  bidst[s]:stdepth sublist (!/) flip x`bids;                                        //get bid state
 }

msg.l2update:{
  /* handle level2 update messages */
  x:"SSZ*"$x;                                                                       //cast dictionary to relevant types
  s:.Q.id x`product_id;                                                             //extract sym, remove bad chars
  c:"SFF"$/:x`changes;                                                              //extract and cast changes
  {.[`.gdax.askst`.gdax.bidst y[0]=`buy;(x;y 1);:;y 2]}[s]'[c];                     //update state dict(s)
  sort.state[s];                                                                    //sort state dicts
  rec.book[x`time;s];                                                               //record current state of book
 }

msg.ticker:{
  /* handle ticker (trade) messages */
  x:"SFFFSZjF"$`product_id`price`best_bid`best_ask`side`time`trade_id`last_size#x;  //cast dict fields
  x:@[x;`product_id;.Q.id];                                                         //fix sym
  x:@[x;`time;"p"$];                                                                //cast time to timestamp
  if[not count x`trade_id;x[`trade_id]:0N];                                         //first rec has empty list
  x:`sym`price`bid`ask`side`time`tid`size!value x;                                  //rename fields
  /rec.trade `time`sym xcols enlist x;                                               //make table & record
  rec.trade x;
  }

upd:{
  /* entrypoint for received messages */
  j:.j.k x;                                                                         //parse received JSON message
  if[(t:`$j[`type]) in key msg;                                                     //check for handler of this message type
     msg[t]j;                                                                       //pass to relevant message handler
    ];
 }

sub:{[h;s;t]
  t:$[t~`;`trade`depth;(),t];                                                       //expand null to all tables, make list
  /* subscribe to l2 data for a given sym */
  if[`depth in t;
     h .j.j `type`product_ids`channels!(`subscribe;enlist string s;enlist"level2"); //send subscription message
  ];
  if[`trade in t;
     h .j.j `type`product_ids`channels!(`subscribe;enlist string s;enlist"ticker"); //send subscription message
  ];
 }

getref:{[]
  r:.req.get["https://api.gdax.com/products";()!()];                                //get reference data using reQ
  :"SSSFFFSSb*FFbbb"$/:r;                                                           //cast to appropriate data types
 }


.gdax.ref:.gdax.getref[];                                                           //get reference data
.gdax.h:.ws.open["wss://ws-feed.gdax.com";`.gdax.upd]                               //open websocket to feed
\
.gdax.sub[.gdax.h;`$"ETH-USD";`];                                                   //subscribe to L2 & trade data for ETH-USD
.gdax.sub[.gdax.h;`$"BTC-GBP";`];                                                   //subscribe to L2 & trade data for BTC-GBP
