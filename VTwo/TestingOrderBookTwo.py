


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

        # Open the file in append mode; create it if it doesn't exist
        with open(file_path, 'a') as json_file:
            # If the file is not empty, write a comma before appending new data
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                json_file.write(",\n")  # Add a comma for JSON formatting

            # Write the new data
            json.dump(data, json_file)  # Use json.dump to write data as JSON
            print("WRITEEN TO ", file_path)

        # if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        #     with open(file_path, 'a') as json_file:
        #         json_file.write(",\n")  # Add a com
                