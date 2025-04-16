import os
import ssl
import certifi
from celery import Celery

UPSTASH_REDIS_URL = os.getenv("UPSTASH_REDIS_URL")

app = Celery('job_tasks',
             broker=UPSTASH_REDIS_URL,
             backend=UPSTASH_REDIS_URL,
             broker_connection_retry_on_startup=True)

app.conf.update(
    broker_use_ssl={
        'ssl_cert_reqs': ssl.CERT_REQUIRED,
        'ssl_ca_certs': certifi.where(),
    },
    redis_backend_use_ssl={
        'ssl_cert_reqs': ssl.CERT_REQUIRED,
        'ssl_ca_certs': certifi.where(),
    },
    task_default_queue='celery',
)
