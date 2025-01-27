


import json
from BookTwo import OrderManager
import os


def AppendBook(book: OrderManager, o_dict, company_id: str):
        data = {
            "buy_orders": [order.__dict__  for order in book.buy_orders],
            "sell_orders": [order.__dict__ for order in book.sell_orders],
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