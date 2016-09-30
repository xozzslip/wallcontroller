from threading import Lock
from default.celery import app
from wallcontroller.models import Community
# lock_access_token = Lock()


@app.task()
def synchronize_community(pk):
    # lock_access_token.acquire()
    Community.objects.get(pk=pk).synchronize()
    # lock_access_token.realise()


@app.task()
def synchronize():
    communities = Community.objects.filter(disabled=False)
    for community in communities:
        community.synchronize()
        tc = community.find_trash_comments()