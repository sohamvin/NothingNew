import time
import datetime

# Get the current time as a timestamp
t = time.time()

def convert_timestamp_to_readable(timestamp):
    # Convert timestamp to a datetime object
    dt_object = datetime.datetime.fromtimestamp(timestamp)  # Use datetime.datetime
    # Format it as a string (you can customize the format as needed)
    return dt_object.strftime('%Y-%m-%d %H:%M:%S')

print(convert_timestamp_to_readable(t))
