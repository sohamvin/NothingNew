#!/usr/bin/env python
import pika, sys, os

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # def callback(ch, method, properties, body):
    #     print(f" [x] Received {body}")

    # channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)

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

    # def callback2(ch, method, properties, body):
    #     print(f"Recived: {body.decode()}")

    #     ch.basic_ack(delivery_tag = method.delivery_tag) #acknowledging that message recived and therfore you 
    #     #can delete message from the queue
    
    # channel.basic_consume(queue='hello', on_message_callback=callback2)

    # print(' [*] Waiting for messages. To exit press CTRL+C')
    # channel.start_consuming()
    channel.queue_declare("task_queue", durable=True)

#         ^^^^^^^^^^^^^^^^^^^^^^^^^^
# pika.exceptions.ChannelClosedByBroker: (406, "PRECONDITION_FAILED - 
# inequivalent arg 'durable' for queue 'hello' in vhost '/': received 'true' but current is 'false'")
# (myvenv) soham@Lalou8ch:~/Documents/OrderBooks/OrderBook$ 
#  In rabits local storage, the hello queue has already been creatd and it now cant be 
#  modified to be durable. you have to create a new queue
#     channel.queue_declare("hello", durable=True)

    def callback3(ch, method, properties, body):
        print(f"Got : {body.decode()}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    #don't dispatch a new message to a worker until it has processed and acknowledged the previous one
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(queue="task_queue", on_message_callback=callback3)

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