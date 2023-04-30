import asyncio
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json


async def consume():
    consumer = AIOKafkaConsumer(
        'my_topic',
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda m: json.loads(m.decode('ascii'))
    )
    await consumer.start()
    try:
        async for msg in consumer:
            print(msg.value)
    finally:
        await consumer.stop()

async def main():
    await asyncio.gather(consume())

if __name__ == '__main__':
    asyncio.run(main())