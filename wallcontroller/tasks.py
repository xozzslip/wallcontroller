from threading import Thread
from queue import Queue
from default.celery import app
from wallcontroller.models import VkAccount


@app.task()
def delete_comments():
    for vkaccount in VkAccount.objects.all():
        vkaccount.update_communities_moderation_statuses()
        tokens_queue = make_tokens_queue(vkaccount)
        threads = []
        for community in vkaccount.community_set.filter(disabled=False,
                                                        under_moderation=True):
            community_task = DeleteCommentsInCommunityTask(community, tokens_queue)
            t = Thread(target=community_task)
            t.start()
            threads.append(t)

    for t in threads:
        t.join()


class DeleteCommentsInCommunityTask:
    def __init__(self, community, tokens_queue):
        self.tokens_queue = tokens_queue
        self.community = community

    def __call__(self):
        with self.community as community:
            community.set_queue(self.tokens_queue)
            community.acquire_token()
            comments = community.get_comments()
            trash_comments = community.find_trash_comments(comments)
            response_list = community.delete_comments(trash_comments)
            community.release_token()
            print("%s %s %s" % (community.title, len(comments), len(response_list)))


def make_tokens_queue(vkaccount):
    queue = Queue()
    for vkapp in vkaccount.vkapp_set.all():
        queue.put(vkapp.access_token)
    return queue
