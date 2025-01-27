import json
import threading

class JsonFileHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.lock = threading.Lock()  # Ensures thread safety

    def GetOrderDetailWithId(self, order_id):
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)


                for entry in data:
                    if entry.get('id') == str(order_id):
                        return entry

                
                # Filter results where buyId or sellId matches the order_id
                # return [
                #     entry for entry in data
                #     if entry.get("buyId") == order_id or entry.get("sellId") == order_id
                # ]
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
        
    def GetElements(self, order_id, name, typee):
        try:
            with open("OBookStatus_" + name + ".json", "r") as file:
                # Read the file content as a string
                file_content = file.read()
                data = json.loads(file_content)  # Now pass the string to json.loads()


                ent = []

                for i, entry in enumerate(data):

                    if i == 0:
                        continue

                    if entry['Incoming_Order']['order_id'] == order_id:
                            ent.append("prev", data[i-1])
                            ent.append(
                                    ("incoming", entry)
                            )
                            continue

                    for k, v in entry[f'{typee}_orders'].items():
                        for ele in v:
                            if ele['order_id'] == order_id:
                                ent.append(
                                    (typee, entry)
                                )
                    # for k, v in entry['sell_orders'].items():
                    #     for ele in v:
                    #         if ele['order_id'] == order_id:
                    #             ent.append(
                    #                 ("sell", entry)
                    #             )


                previous_book = None
                incoming_book = None

                prevcount = None

                for x in ent:
                    if x[0] == "prev":
                        previous_book = x[1]
                    elif x[0] == "incoming":
                        incoming_book = x[1]
                    else:
                        pass


        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(e)
            return {}


    def append(self, new_entry, add=False):
        with self.lock:  # Ensure thread safety during file operations
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
                    if add:

                        json.dump(data + "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n", file, indent=4)
                    else:
                        json.dump(data, file, indent=4)
                
                print("WRITTEN To File")
            except Exception as e:
                print(f"Error appending data: {e}")
