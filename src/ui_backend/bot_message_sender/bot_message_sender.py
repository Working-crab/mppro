
from ui_backend.bot import syncBot
from ui_backend.common import get_reply_markup
import pika, sys, os
import json

from common.appLogger import appLogger
logger = appLogger.getLogger('bot_message_sender')


DEFAULT_MARKUP = 'universal_reply_markup'
CONSUMER_QUEUE = 'bot_message_sender_queue'

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
    syncBot.send_message(destination_id, message, **reply_kwargs)
  except Exception as e:
    logger.error(f' tg send_message error: {e}')
    syncBot.send_message(destination_id, 'На сервере произошла ошибка, попробуйте ещё раз позже или обратитесь к разработчику')


def set_reply_kwarg(reply_kwargs, kwargs, param):
  if kwargs.get(param):
    reply_kwargs[param] = kwargs[param]



def main():

  host='localhost'

  connection = None
  channel = None

  def callback(ch, method, properties, body):
    check_connection()
    body_loaded = json.loads(body)
    logger.info(body_loaded)
    send_message(**body_loaded)

  def check_connection():
    nonlocal connection
    nonlocal channel

    if not connection or connection.is_closed:
      connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
      channel = connection.channel()
      channel.queue_declare(queue=CONSUMER_QUEUE)
      channel.basic_consume(queue=CONSUMER_QUEUE, on_message_callback=callback, auto_ack=True)
      channel.start_consuming()

  check_connection()
  logger.info(' Started, waiting for messages')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)