
from ui_backend.bot import bot
from ui_backend.common import get_reply_markup
import pika, sys, os
import json

from common.appLogger import appLogger
logger = appLogger.getLogger('bot_message_sender')


DEFAULT_MARKUP = 'universal_reply_markup'
CONSUMER_QUEUE = 'bot_message_sender_queue'

def send_message(**kwargs):

  # kwargs['parse_mode'] = 'Markdown'
  destination_id = kwargs['destination_id']
  message = kwargs['message']
  user_id = kwargs['user_id']

  reply_markup_name = ''
  if kwargs.get('reply_markup'):
    reply_markup_name = kwargs['reply_markup']
  else:
    reply_markup_name = DEFAULT_MARKUP
  kwargs["reply_markup"] = get_reply_markup(reply_markup_name, user_id)

  request_message = ''
  if kwargs.get('request_message'):
    request_message = f' request_message: {kwargs.get("request_message")}'

  logger.info(f'destination_id: {destination_id} {request_message} sent_message: {message}')

  bot.send_message(destination_id, message, **kwargs)


def main():
  connection = pika.SelectConnection(pika.ConnectionParameters(host='localhost'))
  channel = connection.channel()

  channel.queue_declare(queue=CONSUMER_QUEUE)

  def callback(ch, method, properties, body):
    body_loaded = json.loads(body)
    print(body_loaded)
    # send_message(**body_loaded)

  channel.basic_consume(queue=CONSUMER_QUEUE, on_message_callback=callback, auto_ack=True)

  logger.info(' Started, waiting for messages')
  channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)