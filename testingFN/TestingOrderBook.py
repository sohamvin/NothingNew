


import json
from Book import OrderBook
import os


def AppendBook(book: OrderBook, o_dict, company_id: str):
        data = {
            "buy_orders": {price: [order.__dict__ for order in orders] for price, orders in book.buy_orders.items()},
            "sell_orders": {price: [order.__dict__ for order in orders] for price, orders in book.sell_orders.items()},
            "Incoming_Order" : o_dict
        }

        file_path = f"OBookStatus_{company_id}.json"

        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'a') as json_file:
                json_file.write(",\n")  # Add a comma to separate JSON objects
                json.dump(data, json_file, indent=4)
                json_file.write("\n\n\n\n\n\n\n\n\n\n\n")  # Additional formatting
        else:
            with open(file_path, 'w') as json_file:
                json_file.write("[\n")
                json.dump([data], json_file, indent=4)  # Write data as a new JSON array