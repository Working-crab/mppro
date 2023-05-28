
from ui_backend.config import syncBot
from ui_backend.common import escape_telegram_specials, get_reply_markup
from kafka_dir.general_consumer import create_async_consumer
from kafka_dir.topics import Topics

import sys, os

import asyncio

from common.appLogger import appLogger
logger = appLogger.getLogger('bot_message_sender')


DEFAULT_MARKUP = 'universal_reply_markup'
CONSUMER_TOPIC = 'telegram_message_sender'

def send_message(**kwargs):

  # kwargs['parse_mode'] = 'Markdown'

  if not kwargs.get('destination_id') or not kwargs.get('message'):
    return

  destination_id = kwargs['destination_id']
  message = kwargs['message']

  reply_markup_name = ''
  if kwargs.get('reply_markup'):
    reply_markup_name = kwargs['reply_markup']
  else:
    reply_markup_name = DEFAULT_MARKUP
  kwargs["reply_markup"] = get_reply_markup(reply_markup_name)

  request_message = ''
  if kwargs.get('request_message'):
    request_message = f' request_message: {kwargs.get("request_message")}'

  logger.info(f'destination_id: {destination_id} {request_message} sent_message: {message}')

  reply_kwargs = {}
  set_reply_kwarg(reply_kwargs, kwargs, 'reply_markup')
  set_reply_kwarg(reply_kwargs, kwargs, 'parse_mode')

  try:
    if kwargs.get('edit'):
      message_id = kwargs.get('message_id')
      message = escape_telegram_specials(message)
      syncBot.edit_message_text(message, destination_id, message_id, parse_mode='MarkdownV2')
    else:
      syncBot.send_message(destination_id, message, **reply_kwargs)
  except Exception as e:
    logger.error(f' tg send_message error: {e}')
    syncBot.send_message(destination_id, 'На сервере произошла ошибка, попробуйте ещё раз позже или обратитесь к разработчику')


def set_reply_kwarg(reply_kwargs, kwargs, param):
  if kwargs.get(param):
    reply_kwargs[param] = kwargs[param]



async def consume():
  consumer = await create_async_consumer(Topics.DEFAULT_TOPIC)
  print('start consume')
  try:
    async for msg in consumer:
      send_message(**msg.value)
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