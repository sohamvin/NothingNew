# #!/usr/bin/env python
# import pika


# #In RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange. 

# # All we need to know now is how to use a default exchange identified by an empty string. 
# # This exchange is special ‒ it allows us to specify exactly to which queue the message should go. 
# # The queue name needs to be specified in the routing_key parameter:

# connection = pika.BlockingConnection(
#     pika.ConnectionParameters(host='localhost'))


# channel = connection.channel()

# channel.queue_declare(queue='hello')

# channel.basic_publish(exchange='', routing_key='hello', body='Hello World!')
# print(" [x] Sent 'Hello World!'")
# connection.close()


#
# To prevent task loss, enable manual acknowledgments in RabbitMQ. 
# Unacknowledged messages are re-queued if a consumer dies, 
# ensuring delivery to another worker. Default acknowledgment timeout is 30 minutes.
#If queue dies, the messages lost. 
#so to prevent that, write periodically to disk.
#to tell queue to do that use = durable=True

#when you first ran code, hello queue was creatd and it as properties
#durable=False.
# Cant change that so create another queue
#  


#!/usr/bin/env python
import pika
import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)

message = ' '.join(sys.argv[1:]) or "Hello World!"
channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=message,
    properties=pika.BasicProperties(
        delivery_mode=pika.DeliveryMode.Persistent #Telling queue to have backup if system goes down
    ))

print(f" [x] Sent {message}")
connection.close()