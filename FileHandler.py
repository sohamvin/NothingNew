import json
import threading

class JsonFileHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        # self.lock = threading.Lock()  # Ensures thread safety

    def search(self, order_id):
        # """
        # Search for all objects with a specific key-value pair in the JSON file.
        # """
        # with self.lock:  # Thread-safe access
            try:
                with open(self.file_path, 'r') as file:
                    data = json.load(file)
                    
                    # Filter results where buyId or sellId matches the order_id
                    return [
                        entry for entry in data
                        if entry.get("buyId") == order_id or entry.get("sellId") == order_id
                    ]
            except (FileNotFoundError, json.JSONDecodeError):
                # Handle missing or corrupted file
                return []

    def append(self, new_entry):
        # """
        # Append a new JSON object to the file.
        # """
        # with self.lock:  # Thread-safe access
            try:
                # Read existing data
                try:
                    with open(self.file_path, 'r') as file:
                        data = json.load(file)
                except (FileNotFoundError, json.JSONDecodeError):
                    data = []  # Initialize empty list if file doesn't exist or is empty
                
                # Append the new entry
                data.append(new_entry)
                
                # Write updated data back to the file
                with open(self.file_path, 'w') as file:
                    json.dump(data, file, indent=4)
            except Exception as e:
                print(f"Error appending data: {e}")

# # Usage Example
# if __name__ == "__main__":
#     handler = JsonFileHandler("data.json")

#     # Append new data
#     new_data = {
#         "buyId": "123",
#         "sellId": "456",
#         "priceMatch": 100.5,
#         "quantityMatch": 20
#     }
#     handler.append(new_data)

#     # Search by buyId
#     results = handler.search("buyId", "123")
#     print(f"Search results for buyId=123: {results}")

#     # Search by sellId
#     results = handler.search("sellId", "456")
#     print(f"Search results for sellId=456: {results}")
