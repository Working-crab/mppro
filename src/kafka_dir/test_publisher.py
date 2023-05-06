import asyncio
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json


async def produce():
    producer = AIOKafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda m: json.dumps(m).encode('ascii')
    )
    await producer.start()
    print('producer started')
    try:
        for i in range(10):
            message = {'value': i}
            await producer.send('my_topic', message)
            await asyncio.sleep(1)
    finally:
        await producer.stop()


async def main():
    await asyncio.gather(produce())

if __name__ == '__main__':
    asyncio.run(main())