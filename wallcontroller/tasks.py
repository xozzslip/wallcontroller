from queue import Queue
from default.celery import app
from wallcontroller.models import Community, VkAccount
from wallcontroller.comments_filter import find_trash_comments


@app.task()
def delete_comments_in_community(pk, queue):
    with Community.objects.get(pk=pk) as community:
        community.acquire_token(queue)
        comments = community.get_comments()
        trash_comments = find_trash_comments(comments)
        response_list = community.delete_comments(trash_comments)
        community.release_token()
        return response_list


@app.task()
def delete_comments():
    communities = Community.objects.filter(disabled=False)[2:3]
    for vkaccounts in VkAccount.objects.all():
    for community in communities:
        pass
        delete_comments_in_community.delay(community.pk, queue)


def make_queue(community):
    queue = Queue()
    for vkapp in community.moderator.vkapp_set.all():
        queue.put(vkapp.access_token)
