import os
import ssl

import cronitor.celery
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
cronitor.api_key = "a338a97cfdef421db4e4c1ac03312f7c"
cronitor.environment = os.getenv("ENVIRONMENT")
app = Celery("core")
if os.getenv("ENVIRONMENT") == "staging":
    app = Celery(
        "core",
        broker_use_ssl={"ssl_cert_reqs": ssl.CERT_NONE},
        redis_backend_use_ssl={"ssl_cert_reqs": ssl.CERT_NONE},
    )
cronitor.celery.initialize(app)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
