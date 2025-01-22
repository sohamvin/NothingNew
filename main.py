from flask import Flask, request, jsonify
import redis
import json

app = Flask(__name__)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)  # Connect to Redis

@app.route('/add_order', methods=['POST'])
def add_order():
    """
    Endpoint to add an order to the Redis queue for the specified company.
    Expects JSON data with order details.
    """
    order = request.json
    # Validate the order format
    required_keys = ['order_id', 'time', 'order_type', 'quantity', 'price', 'company_id']
    if not all(key in order for key in required_keys):
        return jsonify({"error": "Invalid order format"}), 400

    company_id = order['company_id']
    queue_name = f"orders_queue_{company_id}"  # Construct queue name for the company

    # Push order to the company's Redis queue
    redis_client.lpush(queue_name, json.dumps(order))
    return jsonify({"message": f"Order added to queue for company {company_id}"}), 200

if __name__ == "__main__":
    app.run(debug=True)
