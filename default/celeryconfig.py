from datetime import timedelta
BROKER_URL = 'amqp://'


CELERYBEAT_SCHEDULE = {
    'synchronize-communities-every-10-minuits': {
        'task': 'wallcontroller.tasks.synchronize',
        'schedule': timedelta(seconds=60 * 10),
    }
}
