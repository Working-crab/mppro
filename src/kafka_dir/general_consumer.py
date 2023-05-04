from aiokafka import AIOKafkaConsumer
import json


async def create_async_consumer(topic):
  consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda m: json.loads(m.decode('ascii'))
    )
  await consumer.start()
  return consumer

