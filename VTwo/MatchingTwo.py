
import threading
import json
from OrderTwo import Order
from BookTwo import OrderManager
import redis
from TestingOrderBookTwo import AppendBook
from datetime import datetime
import pika.exceptions

import pika
import time


class MatchingEngineTwo:
    def __init__(self, name : str):
        self.order_book = OrderManager()
        self.lock = threading.Lock()

        self.local_redis = redis.Redis(host="localhost", port=6379)
        self.name = name

        # self.channel = None
        # self.connection = None

        self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host='localhost',
                        heartbeat=600,  # Keeps connection alive
                        blocked_connection_timeout=300
                    )
                )
        self.channel = self.connection.channel()

        self.exchange_name = 'order_routing'
        self.complete_delete_exchange = 'complete_delete'
        self.queue_name = f"orders_queue_{self.name}"

        # self.connect()  # Initialize RabbitMQ connection


        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='direct')
        self.channel.exchange_declare(exchange="complete_delete", exchange_type='direct')
        self.channel.queue_declare(queue=self.queue_name, durable=True)
        self.channel.queue_bind(exchange=self.exchange_name, queue=self.queue_name, routing_key=self.queue_name)


        self.channel.queue_declare(queue="COMPLETE", durable=True)
        self.channel.queue_declare(queue="DELETE", durable=True)


        # ✅ Bind the queue to the exchange so it can receive messages
        self.channel.queue_bind(exchange=self.complete_delete_exchange, queue="COMPLETE", routing_key="COMPLETE")
        self.channel.queue_bind(exchange=self.complete_delete_exchange, queue="DELETE", routing_key="DELETE")

        # ✅ Publish message to the exchange with correct routing key


        threading.Thread(target=self.start_rabbitmq_consumer, daemon=True).start()


        self.start_rabbitmq_consumer()

    def start_rabbitmq_consumer(self):
        """ Starts consuming messages from RabbitMQ in a separate thread. """
        queue_name = f"orders_queue_{self.name}"

        with self.lock:

            # print(f" [*] Waiting for messages in queue {queue_name}. To exit, press CTRL+C")
            self.channel.basic_consume(queue=queue_name, on_message_callback=self.process_order_mq, auto_ack=False)
            self.channel.start_consuming()  # This will block the thread but it's in a separate thread

    def process_order_mq(self, ch, method, properties, body):
        """ Processes incoming orders from RabbitMQ queue. """
        try:
            order_dict = json.loads(body)
            # print(f" [x] Received {type(order_dict)} for {order_dict['action']}")

            company_id = order_dict.get("company_id")
            action = order_dict.get("action")

            if action == "delete":
                dictionary = self.order_book.delete_an_order(order_dict["order_id"])
                message = json.dumps(dictionary)
                self.channel.basic_publish(
                    exchange='complete_delete',
                    routing_key="DELETE",  # Route it correctly
                    body=message
                )
            else:
                order = Order(
                    order_id=order_dict["order_id"],
                    time=order_dict["time"],
                    order_type=order_dict["order_type"],
                    quantity=order_dict["quantity"],
                    price=order_dict["price"],
                    company_id=company_id,
                    user_id=order_dict["user_id"]
                )

                array = self.order_book.process_incoming_order(order=order)

                if array:
                    for obj in array:
                        message = json.dumps(obj.__dict__)
                        self.channel.basic_publish(
                            exchange='complete_delete',
                            routing_key="COMPLETE",  # Route it correctly
                            body=message
                        )

                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                (sell_weight, sell_quantity) = self.order_book.weighted_average_sell()
                (buy_weight, buy_quantity) = self.order_book.weighted_average_buy()

                data_to_publish = {
                    "timestamp": current_time,
                    "price": self.algorithm(sell_wt=sell_weight, sell_qt=sell_quantity, buy_qt=buy_quantity, buy_wt=buy_weight)
                }

                if data_to_publish["price"] > 0:
                    try:
                        resp = self.local_redis.xadd(self.name + "_market", data_to_publish)
                        response = self.local_redis.publish(self.name, json.dumps(data_to_publish))
                        print(f"Response to push was: {resp, response}")
                    except Exception as e:
                        print(f"Error adding to stream: {e}")

                # if self.order_book.total_buy_volume > 0:
                    try:
                        resp = self.local_redis.publish(self.name + "_buy_volume", float(self.order_book.total_buy_volume))
                        resp2 = self.local_redis.publish(self.name + "_buy_liquid", float(self.order_book.total_buy_amount))
                        print(f"The response to publishing volume was : {resp} and {resp2}")
                    except Exception as e:
                        print(f"Error offured while publishin : {e}")


                # if self.order_book.total_sell_volume > 0:
                    try:
                        resp = self.local_redis.publish(self.name + "_sell_volume", float(self.order_book.total_sell_volume))
                        resp2 = self.local_redis.publish(self.name + "_sell_liquid", float(self.order_book.total_sell_amount))
                        print(f"The response to publishing volume was : {resp} and {resp2}")
                    except Exception as e:
                        print(f"Error offured while publishin : {e}")

                # AppendBook(self.order_book, order_dict, self.name)
                # print("Also Appended")

            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"Error processing message: {e}")

    def algorithm(self, sell_wt, buy_wt, sell_qt, buy_qt):
        if sell_qt + buy_qt == 0:
            # print("No orders to calculate price.")
            return -1
        
        return (sell_wt+buy_wt)/ (sell_qt + buy_qt)
    

    # def start_rabbitmq_consumer2(self):
    #     """Start consuming messages with auto-reconnection."""
    #     def run_consumer():
    #         while True:
    #             try:
    #                 self.connect()  # Ensure connection is always fresh
    #                 print(f" [*] Waiting for messages in queue {self.queue_name}. To exit, press CTRL+C")

    #                 self.channel.basic_consume(
    #                     queue=self.queue_name,
    #                     on_message_callback=self.process_order_mq,
    #                     auto_ack=False
    #                 )
    #                 self.channel.start_consuming()  # This will block, but will restart on failure
    #             except pika.exceptions.AMQPConnectionError as e:
    #                 print(f"Consumer lost connection: {e}. Reconnecting...")
    #                 time.sleep(5)  # Wait before retrying

    #     threading.Thread(target=run_consumer, daemon=True).start()  # Run consumer in separate thread


    def connect(self):
        """Establish a persistent connection to RabbitMQ with retry logic."""
        while True:
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host='localhost',
                        heartbeat=600,  # Keeps connection alive
                        blocked_connection_timeout=300
                    )
                )
                self.channel = self.connection.channel()
                print("Connected to RabbitMQ!")

                # Declare exchanges & queues (ensures they exist)
                self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='direct')
                self.channel.exchange_declare(exchange=self.complete_delete_exchange, exchange_type='direct')
                self.channel.queue_declare(queue=self.name, durable=True)
                self.channel.queue_bind(exchange=self.exchange_name, queue=self.name, routing_key=self.name)

                self.channel.queue_declare(queue="COMPLETE", durable=True)
                self.channel.queue_declare(queue="DELETE", durable=True)
                self.channel.queue_bind(exchange=self.complete_delete_exchange, queue="COMPLETE", routing_key="COMPLETE")
                self.channel.queue_bind(exchange=self.complete_delete_exchange, queue="DELETE", routing_key="DELETE")

                return  # Exit the retry loop after successful connection
            except pika.exceptions.AMQPConnectionError as e:
                print(f"Connection failed: {e}, retrying in 5 seconds...")
                time.sleep(5)  # Retry connection

