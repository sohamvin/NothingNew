from celery import Celery

app = Celery('order_workers', broker='redis://localhost:6379/0')

# Celery configuration
app.conf.update(
    result_backend='redis://localhost:6379/1',
    timezone='UTC',
    enable_utc=True,
    beat_schedule={}
)
