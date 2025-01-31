import json
import threading
import pika
from FileHandler import JsonFileHandler
import time

class PostProcessor:
    def __init__(self):

        # ✅ File Handlers
        self.writehandle = JsonFileHandler('orders.json')
        self.del_order_handler = JsonFileHandler('delete_orders.json')
        self.added_to_orders = False
        self.added_to_deletes = False
        # ✅ Start Consumers (non-daemon to prevent premature exit)
        threading.Thread(target=self.ConsumeCompleteQUEUE, daemon=False).start()
        threading.Thread(target=self.ConsumeDeleteQUEUE, daemon=False).start()

    def ConsumeCompleteQUEUE(self):
        """ Continuously listen for messages in COMPLETE queue. Reconnect on failure. """
        while True:
            try:
                print(f" [*] Waiting for messages in queue COMPLETE...")
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host='localhost', heartbeat=600)  # ✅ Heartbeat to prevent timeouts
                )
                channel = connection.channel()
                
                channel.exchange_declare(exchange="complete_delete", exchange_type='direct')
                channel.queue_declare(queue="COMPLETE", durable=True)
                channel.queue_bind(exchange='complete_delete', queue="COMPLETE", routing_key="COMPLETE")

                channel.basic_consume(queue="COMPLETE", on_message_callback=self.CallBackComplete, auto_ack=False)
                channel.start_consuming()
            except Exception as e:
                print(f" [!] RabbitMQ Connection Lost (COMPLETE). Reconnecting in 5s... Error: {e}")
                time.sleep(5)  # ✅ Prevent infinite fast loop

    def ConsumeDeleteQUEUE(self):
        """ Continuously listen for messages in DELETE queue. Reconnect on failure. """
        while True:
            try:
                print(f" [*] Waiting for messages in queue DELETE...")
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host='localhost', heartbeat=600)
                )
                channel = connection.channel()
                
                channel.exchange_declare(exchange="complete_delete", exchange_type='direct')
                channel.queue_declare(queue="DELETE", durable=True)
                channel.queue_bind(exchange='complete_delete', queue="DELETE", routing_key="DELETE")

                channel.basic_consume(queue="DELETE", on_message_callback=self.CallBackDelete, auto_ack=False)
                channel.start_consuming()
            except Exception as e:
                print(f" [!] RabbitMQ Connection Lost (DELETE). Reconnecting in 5s... Error: {e}")
                time.sleep(5)

    def CallBackComplete(self, ch, method, properties, body):
        """ Process messages from COMPLETE queue. """
        try:
            order_dict = json.loads(body)
            print(f" [x] Received COMPLETE message: {order_dict} of type : \n\n\n\n{type(order_dict)}")
            self.writehandle.append(order_dict, add=self.added_to_orders)
            self.added_to_orders = True
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Error processing COMPLETE message: {e}")

    def CallBackDelete(self, ch, method, properties, body):
        """ Process messages from DELETE queue. """
        try:
            order_dict = json.loads(body)
            print(f" [x] Received DELETE message: {order_dict}")
            self.del_order_handler.append(order_dict, add=self.added_to_deletes)
            self.added_to_deletes = True
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Error processing DELETE message: {e}")

# ✅ Keep Main Thread Alive
if __name__ == "__main__":
    p = PostProcessor()
    while True:
        time.sleep(1)  # Prevents main thread from exiting