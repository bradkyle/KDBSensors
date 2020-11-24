
spec(
    name='InteractiveBrokersSensor',
    base="",
    kind=ClientType.SENSOR,
    dockerfile="Dockerfile",
    args={
        "host":"",
        "port":"",
        "clientId":"",
        "channels":[""],
        "assets":[]
    }
)
