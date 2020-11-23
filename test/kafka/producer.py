from aiokafka import AIOKafkaProducer
import asyncio
import os

loop = asyncio.get_event_loop()

async def send_many():
    host = os.environ['KAFKA_HOST']
    port = os.environ['KAFKA_PORT']
    topic = os.environ['KAFKA_TOPIC']
    producer = AIOKafkaProducer(
        loop=loop, bootstrap_servers=host+":"+port)
    # Get cluster layout and initial topic/partition leadership information
    await producer.start()
    try:
        # Produce message
        while True:
            await producer.send_and_wait(topic, b"Super message")
    finally:
        # Wait for all pending messages to be delivered or expire.
        await producer.stop()

loop.run_until_complete(send_many())
