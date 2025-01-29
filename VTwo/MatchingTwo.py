
import threading
import json
from OrderTwo import Order
from BookTwo import OrderManager
import redis
from TestingOrderBookTwo import AppendBook
from datetime import datetime

import pika


class MatchingEngineTwo:
    def __init__(self, name : str):
        self.order_book = OrderManager()
        self.lock = threading.Lock()

        self.local_redis = redis.Redis(host="localhost", port=6379)
        self.name = name

        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = connection.channel()

        exchange_name = 'order_routing'
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='direct')
        self.channel.exchange_declare(exchange="complete_delete", exchange_type='direct')
        queue_name = f"orders_queue_{self.name}"
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=queue_name)


        self.channel.queue_declare(queue="COMPLETE", durable=True)
        self.channel.queue_declare(queue="DELETE", durable=True)

        # ✅ Bind the queue to the exchange so it can receive messages
        self.channel.queue_bind(exchange='complete_delete', queue="COMPLETE", routing_key="COMPLETE")
        self.channel.queue_bind(exchange='complete_delete', queue="DELETE", routing_key="DELETE")

        # ✅ Publish message to the exchange with correct routing key


        # threading.Thread(target=self.start_rabbitmq_consumer, daemon=True).start()


        self.start_rabbitmq_consumer()

    def start_rabbitmq_consumer(self):
        """ Starts consuming messages from RabbitMQ in a separate thread. """
        queue_name = f"orders_queue_{self.name}"

        with self.lock:

            print(f" [*] Waiting for messages in queue {queue_name}. To exit, press CTRL+C")
            self.channel.basic_consume(queue=queue_name, on_message_callback=self.process_order_mq, auto_ack=False)
            self.channel.start_consuming()  # This will block the thread but it's in a separate thread

    def process_order_mq(self, ch, method, properties, body):
        """ Processes incoming orders from RabbitMQ queue. """
        try:
            order_dict = json.loads(body)
            print(f" [x] Received {type(order_dict)} for {order_dict['action']}")

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

                if data_to_publish["price"] != 0:
                    try:
                        resp = self.local_redis.xadd(self.name + "_market", data_to_publish)
                        response = self.local_redis.publish(self.name, json.dumps(data_to_publish))
                        print(f"Response to push was: {resp, response}")
                    except Exception as e:
                        print(f"Error adding to stream: {e}")

                # AppendBook(self.order_book, order_dict, self.name)
                # print("Also Appended")

            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"Error processing message: {e}")

    def algorithm(self, sell_wt, buy_wt, sell_qt, buy_qt):
        if sell_qt + buy_qt == 0:
            print("No orders to calculate price.")
            return -1
        
        return (sell_wt+buy_wt)/ (sell_qt + buy_qt)

