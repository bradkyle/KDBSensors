from aiokafka import AIOKafkaConsumer
import asyncio
import os

loop = asyncio.get_event_loop()

async def consume():
    host = os.environ['KAFKA_HOST']
    port = os.environ['KAFKA_PORT']
    group = os.environ['KAFKA_GROUP']
    topic = os.environ['KAFKA_TOPIC']
    consumer = AIOKafkaConsumer(
        topic,
        loop=loop,
        bootstrap_servers=host+":"+port,
        group_id=group)
    # Get cluster layout and join group `my-group`
    await consumer.start()
    try:
        # Consume messages
        async for msg in consumer:
            print("consumed: ", msg.topic, msg.partition, msg.offset,
                  msg.key, msg.value, msg.timestamp)
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()

loop.run_until_complete(consume())
