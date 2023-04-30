
import asyncio

from ui_backend.campaign_info.info_processor import process_campaign

from kafka_dir.general_consumer import create_async_consumer
import sys, os

from common.appLogger import appLogger
logger = appLogger.getLogger('campaign_info_sender')


CONSUMER_TOPIC = 'processing_campaign_info'

async def consume():
  consumer = await create_async_consumer(CONSUMER_TOPIC)
  print(CONSUMER_TOPIC + 'consume')
  try:
    async for msg in consumer:
      process_campaign(**msg.value)
  finally:
    await consumer.stop()

async def main():
  await asyncio.gather(consume())



if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)