
from kafka import KafkaConsumer

consumer = KafkaConsumer('test', bootstrap_servers='127.0.0.1:9092')

for msg in consumer:
  print (msg)
  