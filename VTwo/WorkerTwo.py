import threading
from MatchingTwo import MatchingEngineTwo
import time

class Worker(threading.Thread):
    def __init__(self, company_id):
        super().__init__()
        self.company_id = company_id
        # self.matcher = MatchingEngineTwo(company_id)

    def run(self):
        # Start the continuous push to Redis in a separate thread
        # continuous_thread = threading.Thread(target=self.doContinuous, daemon=True)
        # continuous_thread.start()

        while True:
            try:
                self.matcher = MatchingEngineTwo(self.company_id)
            except Exception as e:
                print(f"Error processing orders for {self.company_id}: {e}")

                
# Function to start workers for all companies.
def start_workers(companies):
    threads = []
    
    for company in companies:
        worker_thread = Worker(company)
        worker_thread.start()
        threads.append(worker_thread)

    return threads

# Example usage: Start workers for all companies.

if __name__ == "__main__":
    companies_list = [
        "Google", "Facebook", "Instagram", "Spotify", "Dropbox", 
        "Reddit", "Netflix", "Pinterest", "Quora", "YouTube", 
        "Lyft", "Uber", "LinkedIn", "Slack", "Etsy", 
        "Mozilla", "NASA", "IBM", "Intel", "Microsoft"
    ]

    
    workers = start_workers(companies_list)






