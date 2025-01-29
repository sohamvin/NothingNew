# # from flask import Flask, request, jsonify
# # import redis
# # import json

# # app = Flask(__name__)
# # redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)  # Connect to Redis

# # @app.route('/add_order', methods=['POST'])
# # def add_order():
# #     """
# #     Endpoint to add an order to the Redis queue for the specified company.
# #     Expects JSON data with order details.
# #     """
# #     order = request.json
# #     # Validate the order format
# #     required_keys = ['order_id', 'time', 'order_type', 'quantity', 'price', 'company_id']
# #     if not all(key in order for key in required_keys):
# #         return jsonify({"error": "Invalid order format"}), 400

# #     company_id = order['company_id']
# #     queue_name = f"orders_queue_{company_id}"  # Construct queue name for the company

# #     # Push order to the company's Redis queue
# #     redis_client.lpush(queue_name, json.dumps(order))
# #     return jsonify({"message": f"Order added to queue for company {company_id}"}), 200

# # if __name__ == "__main__":
# #     app.run(debug=True)


# from flask import Flask, request, jsonify
# import redis
# import json

# app = Flask(__name__)
# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)  # Connect to Redis

# @app.route('/add_order', methods=['POST'])
# def add_order():
#     """
#     Endpoint to add an order to the Redis queue for the specified company.
#     Expects JSON data with order details.
#     """
#     order = request.json
#     required_keys = ['order_id', 'time', 'order_type', 'quantity', 'price', 'company_id']
    
#     if not all(key in order for key in required_keys):
#         return jsonify({"error": "Invalid order format"}), 400

#     company_id = order['company_id']
#     queue_name = f"orders_queue_{company_id}"  # Construct queue name for the company

#     # Push order to the company's Redis queue
#     redis_client.lpush(queue_name, json.dumps(order))
#     return jsonify({"message": f"Order added to queue for company {company_id}"}), 200

# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask, request, jsonify
import redis
import json
import time
app = Flask(__name__)
import pika
"""Basic connection example.
"""

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='order_routing', exchange_type='direct')

import sys


redis_client = redis.Redis(
        host='redis-16758.c264.ap-south-1-1.ec2.redns.redis-cloud.com',
        port=16758,
        decode_responses=True,
        username="default",
        password="hTg4EOmVoo4h1OAncK2pAk5RNCFP6XD9",
    )



@app.route('/add_order', methods=['POST'])
def add_order():
    """
    Endpoint to add an order to the Redis queue for the specified company.
    Expects JSON data with order details.
    """
    order = request.json
    required_keys = ['order_id', 'time', 'order_type', 'quantity', 'price', 'company_id']
    
    if not all(key in order for key in required_keys):
        return jsonify({"error": "Invalid order format"}), 400

    company_id = order['company_id']
    queue_name = f"orders_queue_{company_id}"  # Construct queue name for the company
    order["action"] = "add"

    channel.queue_declare(queue=queue_name, durable=True)

    # ✅ Bind the queue to the exchange so it can receive messages
    channel.queue_bind(exchange='order_routing', queue=queue_name, routing_key=queue_name)

    # ✅ Publish message to the exchange with correct routing key
    message = json.dumps(order)
    channel.basic_publish(
        exchange='order_routing',
        routing_key=queue_name,  # Route it correctly
        body=message
    )
    print(f" [x] Sent {queue_name}:{message}")
    # connection.close()

    # Push order to the company's Redis queue
    # redis_client.lpush(queue_name, json.dumps(order))
    return jsonify({"message": f"Order added to queue for company {company_id}"}), 200


@app.route('/delete_order', methods=['DELETE'])
def delete_order():
    """
    Endpoint to delete an order from the Redis queue for the specified company.
    Expects JSON data with order details.
    """
    order = request.json
    required_keys = ['order_id', 'order_procedure', 'price', 'company_id', 'time']

    if not all(key in order for key in required_keys):
        return jsonify({"error": "Invalid delete request format"}), 400

    order_id = order['order_id']
    company_id = order['company_id'] 
    queue_name = f"orders_queue_{company_id}"  # Construct queue name for the company

    # Create a deletion message (you can customize this as needed)
    delete_message = {
        "action": "delete",
        "order_id": order_id,
        "price": order['price'],
        "timestamp": time.time(),  # Optional: include a timestamp
        "order_type" : order["order_procedure"],
        "time" : order['time']

    }

    # Push delete action to the company's Redis queue
    redis_client.lpush(queue_name, json.dumps(delete_message))
    
    return jsonify({"message": f"Order deletion request added to queue for company {company_id}"}), 200


if __name__ == '__main__':
    app.run(debug=True)

