
# TODO binance agent 
# TODO binance futures agent
# TODO binance futures cron agent

spec(
    name='BinanceWssSensor',
    base="",
    kind="",
    files = [
        "spotwss"
    ],
    args={
        "url":"",
        "channels":[""],
        "assets":[]
    }
)

spec(
    name='BinanceAuthWssSensor',
    kind="",
)

spec(
    name='BinanceFuturesWssSensor',
    kind="",
)

spec(
    name='BinanceAuthFuturesWssSensor',
    kind="",
)

spec(
    name='BinanceFuturesCronSensor',
    kind="",
)

spec(
    name='BinanceEffector',
    kind="",
)

spec(
    name='BinanceFuturesEffector',
    kind="",
)

