
.binance.spot.parsers.trade :{[]
				  
				  
				};

.binance.spot.parsers.depth :{[]
				  
				  
				};

.binance.spot.subs:{[]
				  
				  
				};

.sensor.WSSSensor[
	"binancefutures";
	"wss://stream.binance.com:9443/stream?streams=";
	.binance.spot.subs;
	.binance.spot.parsers
	];
