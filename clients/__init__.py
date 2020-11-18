from clients.registration import registry, register, make, spec

# binance  
#--------------------------------------------> 

register(
    id='BinanceWssSensor',
    entry_point='beast.clients.binance:BinanceWssSensor',
)

register(
    id='BinanceAuthWssSensor',
    entry_point='beast.clients.binance:BinanceWssSensor',
)

register(
    id='BinanceFuturesWssSensor',
    entry_point='beast.clients.binance:BinanceFuturesWssSensor',
)

register(
    id='BinanceAuthFuturesWssSensor',
    entry_point='beast.clients.binance:BinanceFuturesWssSensor',
)

register(
    id='BinanceFuturesCronSensor',
    entry_point='beast.clients.binance:BinanceFuturesCronSensor',
)

register(
    id='BinanceEffector',
    entry_point='beast.clients.binance:BinanceEffector',
)

register(
    id='BinanceFuturesEffector',
    entry_point='beast.clients.binance:BinanceFuturesEffector',
)


# bitmex 
#--------------------------------------------> 

register(
    id='BitmexWssSensor',
    entry_point='beast.clients.bitmex:BitmexWssSensor',
)

register(
    id='BitmexAuthWssSensor',
    entry_point='beast.clients.bitmex:BitmexAuthWssSensor',
)

register(
    id='BitmexEffector',
    entry_point='beast.clients.bitmex:BitmexEffector',
)

# okex 
#--------------------------------------------> 

register(
    id='BinanceWssSensor',
    entry_point='beast.clients.binance:BinanceWssSensor',
)

register(
    id='BinanceAuthWssSensor',
    entry_point='beast.clients.binance:BinanceWssSensor',
)

register(
    id='BinanceFuturesWssSensor',
    entry_point='beast.clients.binance:BinanceFuturesWssSensor',
)

register(
    id='BinanceAuthFuturesWssSensor',
    entry_point='beast.clients.binance:BinanceFuturesWssSensor',
)

register(
    id='BinanceFuturesCronSensor',
    entry_point='beast.clients.binance:BinanceFuturesCronSensor',
)

register(
    id='BinanceEffector',
    entry_point='beast.clients.binance:BinanceEffector',
)

register(
    id='BinanceFuturesEffector',
    entry_point='beast.clients.binance:BinanceFuturesEffector',
)

# coinbase 
#--------------------------------------------> 

# huobi 
#--------------------------------------------> 

# twitter 
#--------------------------------------------> 

# interactive brokers 
#--------------------------------------------> 

# iqfeed 
#--------------------------------------------> 

# rss 
#--------------------------------------------> 

# betfair 
#--------------------------------------------> 

# polygon 
#--------------------------------------------> 

# youtube 
#--------------------------------------------> 

# pushshift 
#--------------------------------------------> 

# tradingview 
#--------------------------------------------> 

# bloomberg 
#--------------------------------------------> 

# okcoin 
#--------------------------------------------> 

# kraken 
#--------------------------------------------> 

# deribit 
#--------------------------------------------> 

# robinhood 
#--------------------------------------------> 
