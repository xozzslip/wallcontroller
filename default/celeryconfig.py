from datetime import timedelta
BROKER_URL = 'amqp://'


CELERYBEAT_SCHEDULE = {
    'synchronize-communities-every-10-minuits': {
        'task': 'wallcontroller.tasks.delete_comments',
        'schedule': timedelta(seconds=60 * 5),
    }
}
CELERY_ALWAYS_EAGER = False
