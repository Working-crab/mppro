
import json
from pika.exchange_type import ExchangeType

from common.appLogger import appLogger

LOGGER = appLogger.getLogger('mq_campaign_info')

class ExamplePublisher(object):
    EXCHANGE = 'campaign_info_queue'
    EXCHANGE_TYPE = ExchangeType.topic
    PUBLISH_INTERVAL = 0.1
    QUEUE = 'campaign_info_queue'
    ROUTING_KEY = 'campaign_info_queue'

import aio_pika
import aio_pika.abc
import asyncio
from typing import Optional


connection: Optional[aio_pika.RobustConnection] = None
channel: Optional[aio_pika.abc.AbstractChannel] = None
messages = asyncio.Queue()
running = True


async def main(loop=None):
    connection_url = 'amqp://guest:guest@localhost:5672/%2F?connection_attempts=3&heartbeat=3600'
    global connection, channel
    
    LOGGER.info('Connecting to %s', connection_url)
    connection = await aio_pika.connect_robust(connection_url, loop=loop)
    LOGGER.info('Connection opened')
    
    LOGGER.info('Creating a new channel')
    channel = await connection.channel()
    LOGGER.info('Channel opened')

    LOGGER.info('Declaring exchange %s', ExamplePublisher.EXCHANGE)
    exchange = await channel.declare_exchange(ExamplePublisher.EXCHANGE, aio_pika.ExchangeType.TOPIC)
    LOGGER.info('Exchange declared: %s', ExamplePublisher.EXCHANGE)

    queue_name = ExamplePublisher.QUEUE
    LOGGER.info('Declaring queue %s', queue_name)
    queue = await channel.declare_queue(queue_name)

    routing_key = ExamplePublisher.ROUTING_KEY
    LOGGER.info('Binding %s to %s with %s', ExamplePublisher.EXCHANGE,
        ExamplePublisher.QUEUE, routing_key)
    await queue.bind(exchange, routing_key=routing_key)
    LOGGER.info('Queue bound')

    LOGGER.info('Issuing consumer related RPC commands')
    # ...

    # LOGGER.info('Put test message to queue')
    # await messages.put({
    #     'message': "Hello! I'm a test message.",
    #     #'destination_id': 898912046,  # vadim
    #     #'destination_id': 281746538,  # sasha
    #     #'user_id': 281746538,
    # })

    while running:
        message = await messages.get()

        LOGGER.info('Publish message from queue')
        await exchange.publish(aio_pika.Message(
            json.dumps(message, ensure_ascii=False).encode('utf-8'),
            content_type='application/json',
            app_id='example-publisher'
        ), routing_key)
        LOGGER.info('Message published')


async def queue_message_async(**kwargs):
    await messages.put(kwargs)


def queue_message_sync(**kwargs):
    messages.put_nowait(kwargs)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
