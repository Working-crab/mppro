
import pika, json

PUBLISHER_QUEUE = 'bot_message_sender_queue'

message_queue_connection = pika.SelectConnection(
    pika.ConnectionParameters(host='localhost'))
    
channel = message_queue_connection.channel()
channel.queue_declare(queue=PUBLISHER_QUEUE)

def queue_message(**kwargs):

  if (not kwargs.get('destination_id') 
      or not kwargs.get('message')
      or not kwargs.get('user_id')
    ):
    raise Exception('Не передаются обязательные поля queue_message!')

  body = json.dumps(kwargs)

  channel.basic_publish(exchange='', routing_key=PUBLISHER_QUEUE, body=body)
