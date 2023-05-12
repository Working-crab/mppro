import asyncio
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json

from common.appLogger import appLogger
logger = appLogger.getLogger(__name__)

producer = {}
DEFAULT_TOPIC = 'telegram_message_sender'

async def create_async_producer():
  producer = AIOKafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda m: json.dumps(m).encode('ascii')
  )
  await producer.start()
  return producer




async def queue_message_async(**kwargs):
  logger.warn(123)
  global producer
  if not producer:
    producer = await create_async_producer()
  
  topic = kwargs.get('topic', DEFAULT_TOPIC)
  await producer.send(topic, kwargs)

  



# def queue_message_sync(**kwargs):
#   messages.put_nowait(kwargs)
