
.binance.futures.parsers.depthUpdate :{[]
				  
				  
				};

.binance.futures.parsers.markPriceUpdate :{[]
				  
				  
				};

.binance.futures.parsers.compositeIndex :{[]
				  
				  
				};

.binance.futures.parsers.24hrTicker :{[]
				  
				  
				};

.binance.futures.parsers.forceOrder :{[]
				  
				  
				};

.binance.futures.parsers.kline :{[]
				  
				  
				};

.binance.futures.parsers.aggTrade :{[]
				  
				  
				};

.binance.futures.subs:{[]
				  
				  
				};


.sensor.WSSSensor[
	"binancefutures";
	"wss://stream.binance.com:9443/stream?streams=";
	.binance.futures.subs;
	.binance.futures.parsers
	];
