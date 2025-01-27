
import threading
import json
from OrderTwo import Order
from BookTwo import OrderManager
import redis
from TestingOrderBookTwo import AppendBook

class MatchingEngineTwo:
    def __init__(self, name : str):
        self.order_book = OrderManager()
        self.lock = threading.Lock()
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0) 
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

                AppendBook(self.order_book, order_dict, self.name)






