

.binance.MARGIN_CALL :{[]
				  
				  
				};

.binance.ACCOUNT_UPDATE :{[]
				  
				  
				};

.binance.ORDER_TRADE_UPDATE :{[]
				  
				  
				};

.binance.futures.subs:{[]
				  
				  
				};

.sensor.WSSSensor[
	"binancefutures";
	"wss://stream.binance.com:9443/stream?streams=";
	.binance.futures.subs;
	.binance.futures.parsers
	];
