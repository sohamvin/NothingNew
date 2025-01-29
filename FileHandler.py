import json
import threading

class JsonFileHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.lock = threading.Lock()  # Ensures thread safety
    def append(self, new_entry, add=False):
        with self.lock:  # Ensure thread safety during file operations
            try:

                print(f" \n\n\n\n\n\n\n\\n\n\n\n\n\n\n\n\n\n\n\n\n data Type of {new_entry} : {type(new_entry)} \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
                
                # Read existing data
                try:
                    with open(self.file_path, 'r') as file:
                        data = json.load(file)
                except (FileNotFoundError, json.JSONDecodeError):
                    data = []  # Initialize empty list if file doesn't exist or is empty
                

                print(f" \n\n\n\n\n\n\n\\n\n\n\n\n\n\n\n\n\n\n\n\n data Type of {data} : {type(data)} \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
                
                # # Append the new entry
                # data.append(new_entry)


                # # Write updated data back to the file
                # with open(self.file_path, 'w') as file:
                #     if add:
                #         file.write(json.dumps(data, indent=4))  # ✅ Corrected
                #         file.write("\n\n\n\n\n\n\n")
                #     else:
                #         json.dump(data, file, indent=4)
                
                # print("WRITTEN To File")
            except Exception as e:
                print(f"Error appending data: {e}")
