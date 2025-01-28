
import threading
import json
from OrderTwo import Order
from BookTwo import OrderManager
import redis
from TestingOrderBookTwo import AppendBook
from datetime import datetime

class MatchingEngineTwo:
    def __init__(self, name : str):
        self.order_book = OrderManager()
        self.lock = threading.Lock()
        self.redis_client = redis.Redis(
        host='redis-16758.c264.ap-south-1-1.ec2.redns.redis-cloud.com',
        port=16758,
        decode_responses=True,
        username="default",
        password="hTg4EOmVoo4h1OAncK2pAk5RNCFP6XD9",
    )
        self.local_redis = redis.Redis(host="localhost", port=6379)

        # self.running = True
        # threading.Thread(target=self.push_order_book_to_redis, daemon=True).start()
        self.name = name

    def read_from_queue(self):
        with self.lock:

            while True:
                
                queue_name = f"orders_queue_{self.name}"

                order_data = self.redis_client.brpop(queue_name)

                if not order_data:
                    continue

                _, data = order_data  # Unpack tuple returned by brpop
                order_dict = json.loads(data)

                if order_dict["action"] == "delete":
                    dictionary = self.order_book.delete_an_order(order_dict["order_id"])
                    json_data = json.dumps(dictionary, indent=4)
                    self.redis_client.lpush("DELETE", json_data)

                else:
                    order = Order(
                        order_id=order_dict["order_id"],
                        time=order_dict["time"],
                        order_type=order_dict["order_type"],
                        quantity=order_dict["quantity"],
                        price=order_dict["price"],
                        company_id=order_dict["company_id"],
                        user_id=order_dict["user_id"]

                    )

                    array = self.order_book.process_incoming_order(order=order)

                    if array:
                        for obj in array:
                            self.redis_client.lpush("COMPLETE", json.dumps(obj.__dict__))
                    

                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Serialize the order book and calculate weighted averages
                (sell_weight, sell_quantity) = self.order_book.weighted_average_sell()
                (buy_weight, buy_quantity) = self.order_book.weighted_average_buy()



                # Prepare the data to publish
                data_to_publish = {
                    "timestamp": current_time,
                    "price" : self.algorithm(sell_wt=sell_weight, sell_qt=sell_quantity, buy_qt=buy_quantity, buy_wt=buy_weight)
                }

                # Publish the data as a JSON string
                response = self.local_redis.publish(self.name, json.dumps(data_to_publish))

                print(f"Responce to push was {response}")

                AppendBook(self.order_book, order_dict, self.name)

                print(f"Also Appended")


    def algorithm(self, sell_wt, buy_wt, sell_qt, buy_qt):
        if sell_qt + buy_qt == 0:
            print("No orders to calculate price.")
            return -1
        
        return (sell_wt+buy_wt)/ (sell_qt + buy_qt)


    def push_order_book_to_redis(self):
        with self.lock:
            try:

                # Serialize the order book and push it to Redis.
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Serialize the order book and calculate weighted averages
                (sell_weight, sell_quantity) = self.order_book.weighted_average_sell()
                (buy_weight, buy_quantity) = self.order_book.weighted_average_buy()

                # Prepare the data to publish
                data_to_publish = {
                    "timestamp": current_time,
                    "price" : self.algorithm(sell_wt=sell_weight, sell_qt=sell_quantity, buy_qt=buy_quantity, buy_wt=buy_weight)
                }

                # Publish the data as a JSON string
                self.redis_client.publish(self.name, json.dumps(data_to_publish))

                # serialized_book = json.dumps(self.order_book.serialize(), indent=4)
                # self.redis_client.set(f"order_book_{self.name}", serialized_book)
                print(f"Pushed to redis publisher{self.name}\n\n\n\n\n\n\n\n")
            except Exception as e:
                print(f"Error pushing order book to Redis for {self.name}: {e}")
            # finally:
            #     # Schedule the next execution.
            #     threading.Timer(30, self.push_order_book_to_redis).start()






