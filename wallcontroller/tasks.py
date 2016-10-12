import queue

from default.celery import app
from wallcontroller.models import Community
from wallcontroller.comments_filter import find_trash_comments

queue = queue.Queue()


@app.task()
def synchronize_community(pk):
    Community.objects.get(pk=pk)


@app.task()
def delete_comments():
    communities = Community.objects.filter(disabled=False)
    for community in communities:
        comments = community.get_comments()
        trash_comments = find_trash_comments(comments)
        return trash_comments
