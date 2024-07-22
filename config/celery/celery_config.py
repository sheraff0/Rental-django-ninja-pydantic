from datetime import timedelta

from django.conf import settings

timezone = settings.TIME_ZONE
task_track_started = True
task_time_limit = 30 * 60

broker_url = settings.REDIS_URL
result_backend = broker_url
broker_connection_retry_on_startup = True

imports = (
    "bridge.tasks",
    "api.bookings.tasks",
    "api.auth.tasks",
)

beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"

beat_schedule = {
    "import_all": {
        "task": "bridge.tasks.import_all",
        "schedule": timedelta(hours=6),
        "options": {
            "expires": timedelta(minutes=20),
        },
    },
    "set_expired_bookings": {
        "task": "api.bookings.tasks.set_expired_bookings_task",
        "schedule": timedelta(minutes=1),
        "options": {
            "expires": timedelta(minutes=20),
        },
    },
    "update_unsettled_payments_status": {
        "task": "api.bookings.tasks.update_unsettled_payments_status_task",
        "schedule": timedelta(minutes=1),
        "options": {
            "expires": timedelta(minutes=20),
        },
    },
    "clear_unused_guest_accounts": {
        "task": "api.auth.tasks.clear_unused_guest_accounts_task",
        "schedule": timedelta(hours=12),
        "options": {
            "expires": timedelta(minutes=20),
        },
    },
}
