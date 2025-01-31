import threading
import json
import time
import redis
import pika
from datetime import datetime
from OrderTwo import Order
from BookTwo import OrderManager
import pika.exceptions

class MatchingEngineTwo:
    def __init__(self, name: str):
        self.name = name
        self.order_book = OrderManager()
        self.lock = threading.Lock()
        
        self.local_redis = self.connect_redis()  # Initialize Redis
        self.channel = None
        self.connection = None
        self.exchange_name = 'order_routing'
        self.complete_delete_exchange = 'complete_delete'
        self.queue_name = f"orders_queue_{self.name}"
        
        self.connect_rabbitmq()  # Initialize RabbitMQ connection

        # Start consuming messages in a separate thread
        consumer_thread = threading.Thread(target=self.start_rabbitmq_consumer, daemon=True, name=f"RabbitMQConsumer-{self.name}")
        consumer_thread.start()

    def connect_redis(self):
        while True:
            try:
                redis_client = redis.Redis(host="localhost", port=6379, socket_connect_timeout=5)
                redis_client.ping()  # Check connection
                print(f"✅ Connected to Redis for {self.name}")
                return redis_client
            except redis.ConnectionError:
                print("❌ Redis connection failed, retrying in 5 seconds...")
                time.sleep(5)

    def connect_rabbitmq(self):
        while True:
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host='localhost',
                        heartbeat=600,  # Keep alive
                        blocked_connection_timeout=300
                    )
                )
                self.channel = self.connection.channel()
                self.setup_rabbitmq()
                print(f"✅ Connected to RabbitMQ for {self.name}")
                return
            except (pika.exceptions.AMQPConnectionError, pika.exceptions.ChannelClosedByBroker) as e:
                print(f"❌ RabbitMQ connection failed for {self.name}: {e}, retrying in 30 seconds...")
                time.sleep(30)

    def setup_rabbitmq(self):
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='direct')
        self.channel.exchange_declare(exchange=self.complete_delete_exchange, exchange_type='direct')
        self.channel.queue_declare(queue=self.queue_name, durable=True)
        self.channel.queue_bind(exchange=self.exchange_name, queue=self.queue_name, routing_key=self.queue_name)
        self.channel.queue_declare(queue="COMPLETE", durable=True)
        self.channel.queue_declare(queue="DELETE", durable=True)
        self.channel.queue_bind(exchange=self.complete_delete_exchange, queue="COMPLETE", routing_key="COMPLETE")
        self.channel.queue_bind(exchange=self.complete_delete_exchange, queue="DELETE", routing_key="DELETE")

    def start_rabbitmq_consumer(self):
        while True:
            try:
                print(f"📡 Listening for messages in {self.queue_name}")
                self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.process_order_mq, auto_ack=False)
                self.channel.start_consuming()
            except (pika.exceptions.AMQPConnectionError, pika.exceptions.ChannelClosedByBroker) as e:
                print(f"❌ RabbitMQ Consumer for {self.name} disconnected: {e}, reconnecting...")
                self.connect_rabbitmq()  # Reconnect and restart consuming

    def process_order_mq(self, ch, method, properties, body):
        try:
            order_dict = json.loads(body)
            action = order_dict.get("action")

            if action == "delete":
                dictionary = self.order_book.delete_an_order(order_dict["order_id"])
                self.channel.basic_publish(exchange='complete_delete', routing_key="DELETE", body=json.dumps(dictionary))
            else:
                order = Order(
                    order_id=order_dict["order_id"],
                    time=order_dict["time"],
                    order_type=order_dict["order_type"],
                    quantity=order_dict["quantity"],
                    price=order_dict["price"],
                    company_id=order_dict.get("company_id"),
                    user_id=order_dict["user_id"]
                )

                array = self.order_book.process_incoming_order(order=order)
                if array:
                    for obj in array:
                        self.channel.basic_publish(exchange='complete_delete', routing_key="COMPLETE", body=json.dumps(obj.__dict__))

                self.update_redis()

            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"❌ Error processing message: {e}")

    def update_redis(self):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        (sell_weight, sell_quantity) = self.order_book.weighted_average_sell()
        (buy_weight, buy_quantity) = self.order_book.weighted_average_buy()
        price = self.algorithm(sell_weight, buy_weight, sell_quantity, buy_quantity)

        if price > 0:
            data_to_publish = {
                "time": current_time,
                "price": price,
            }
            try:
                self.local_redis.xadd(self.name + "_market", data_to_publish)
                response = self.local_redis.publish(self.name, json.dumps(data_to_publish))
                print(f"Response to push was: {response}")

                self.local_redis.publish(self.name + "_buy_volume", float(self.order_book.total_buy_volume))
                self.local_redis.publish(self.name + "_buy_liquid", float(self.order_book.total_buy_amount))
                self.local_redis.publish(self.name + "_sell_volume", float(self.order_book.total_sell_volume))
                self.local_redis.publish(self.name + "_sell_liquid", float(self.order_book.total_sell_amount))
            except redis.ConnectionError:
                print("❌ Redis connection lost, reconnecting...")
                self.local_redis = self.connect_redis()

    def algorithm(self, sell_wt, buy_wt, sell_qt, buy_qt):
        if sell_qt + buy_qt == 0:
            return -1
        return (sell_wt + buy_wt) / (sell_qt + buy_qt)