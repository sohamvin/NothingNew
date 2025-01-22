from celery_config import app
from Worker import process_orders  # Import the task

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Set up periodic tasks to run workers for all companies every minute.
    """
    companies = [
        "Google", "Facebook", "Instagram", "Spotify", "Dropbox",
        "Reddit", "Netflix", "Pinterest", "Quora", "YouTube",
        "Lyft", "Uber", "LinkedIn", "Slack", "Etsy",
        "Mozilla", "NASA", "IBM", "Intel", "Microsoft"
    ]

    for company in companies:
        sender.add_periodic_task(
            10.0,  # Run every 60 seconds
            process_orders.s(company),
            name=f"Process orders for {company}"
        )
