from default.celery import app
from wallcontroller.models import Community


@app.task()
def synchronize(name='wallcontroller.tasks.synchronize'):
    communities = Community.objects.filter(disabled=False)
    for community in communities:
        community.synchronize()
    return 'OK'
