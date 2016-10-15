import multiprocessing.dummy
from default.celery import app
from wallcontroller.models import Community, VkAccount
from wallcontroller.comments_filter import find_trash_comments


@app.task()
def delete_comments_in_community(pk, queue):
    with Community.objects.get(pk=pk) as community:
        community.set_queue(queue)
        community.acquire_token()
        comments = community.get_comments()
        trash_comments = find_trash_comments(comments)
        response_list = community.delete_comments(trash_comments)
        community.release_token()
        return response_list


@app.task()
def delete_comments():
    for vkaccount in VkAccount.objects.all():
        queue = make_queue(vkaccount)
        for community in vkaccount.community_set.filter(disabled=False):
            delete_comments_in_community.delay(community.pk, queue)


def make_queue(vkaccount):
    manager = multiprocessing.dummy.Manager()
    queue = manager.Queue()
    for vkapp in vkaccount.vkapp_set.all():
        queue.put(vkapp.access_token)
    return queue
