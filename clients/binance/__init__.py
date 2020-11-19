
# TODO binance agent 
# TODO binance futures agent
# TODO binance futures cron agent

spec(
    name='BinanceWssSensor',
    kind="",
    entry_point='beast.clients.binance:BinanceWssSensor',
)

spec(
    name='BinanceAuthWssSensor',
    kind="",
    entry_point='beast.clients.binance:BinanceWssSensor',
)

spec(
    name='BinanceFuturesWssSensor',
    kind="",
    entry_point='beast.clients.binance:BinanceFuturesWssSensor',
)

spec(
    name='BinanceAuthFuturesWssSensor',
    kind="",
    entry_point='beast.clients.binance:BinanceFuturesWssSensor',
)

spec(
    name='BinanceFuturesCronSensor',
    kind="",
    entry_point='beast.clients.binance:BinanceFuturesCronSensor',
)

spec(
    name='BinanceEffector',
    kind="",
    entry_point='beast.clients.binance:BinanceEffector',
)

spec(
    name='BinanceFuturesEffector',
    kind="",
    entry_point='beast.clients.binance:BinanceFuturesEffector',
)

