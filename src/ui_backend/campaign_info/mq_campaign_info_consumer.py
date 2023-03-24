
import asyncio
import aio_pika

from ui_backend.message_queue import main as message_queue
from ui_backend.mq_campaign_info import main as mq_campaign_info

from rabbit.rabbit import connection_url
from ui_backend.campaign_info.info_processor import process_campaign

from common.appLogger import appLogger
logger = appLogger.getLogger('mq_campaign_info_sender')

CONSUMER_QUEUE = 'campaign_info_queue'

async def main(loop=None):

  loop = asyncio.get_running_loop()
  asyncio.create_task(message_queue(loop))
  asyncio.create_task(mq_campaign_info(loop))

  # coros = [message_queue(loop), mq_campaign_info(loop)]
  # await asyncio.gather(*coros)

  connection = await aio_pika.connect_robust(connection_url, loop=loop)
  queue_name = CONSUMER_QUEUE

  async with connection:
    channel = await connection.channel()

    await channel.set_qos(prefetch_count=10)

    queue = await channel.declare_queue(queue_name) # auto_delete=False

    async with queue.iterator() as queue_iter:
      async for message in queue_iter:
        async with message.process():

          logger.info('body')
          logger.info(message.body)

          process_campaign(message.body)
  
  while True:
    await asyncio.sleep(1)

if __name__ == "__main__":
  print(123)
  logger.info(123)

  asyncio.run(main())
  # loop = asyncio.get_event_loop()
  # loop.run_until_complete(main(loop))
  # loop.close()
