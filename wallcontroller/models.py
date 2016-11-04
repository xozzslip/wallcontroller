import time
from threading import Lock
from django.db import models
from django.contrib.auth.models import User
from vk.commands import get_group, get_groups_under_moderation
from vk.custom_api import PublicApiCommands
from wallcontroller.comments_filter import likes_function


def sync(func):
    def wrapper(self):
        lock = Lock()
        lock.acquire()
        func(self)
        lock.release()
    return wrapper


class Community(models.Model):
    url = models.CharField(max_length=300, null=True, blank=True)
    domen = models.IntegerField(null=True, blank=True)
    domen_name = models.CharField(max_length=300)
    title = models.CharField(max_length=300, null=True, blank=True)
    pic_url = models.CharField(max_length=300, null=True, blank=True)
    user_owner = models.ForeignKey(User)
    moderator = models.ForeignKey("VkAccount", blank=True, null=True)

    post_count_for_synchronize = models.IntegerField(default=50)
    disabled = models.BooleanField(default=True)
    under_moderation = models.BooleanField(default=False)

    turnedon_ts = models.IntegerField(default=0)
    clean_only_new_posts = models.BooleanField(default=True)

    end_count = models.IntegerField(default=1)
    end_time = models.IntegerField(default=60 * 60)
    loyal_time = models.IntegerField(default=60 * 10)

    access_token = ""
    queue = None

    @property
    def api(self):
        return PublicApiCommands(access_token=self.access_token, domen=self.domen)

    def get_posts(self, count):
        return self.api.get_post_list(count)

    def create_post(self, text):
        return self.api.create_post(text)

    def delete_post(self, post_id):
        return self.api.delete_post(post_id)

    def get_comments_from_post_list(self, posts):
        return self.api.get_comments_from_post_list(posts)

    def get_comments_form_post(self, post_id):
        return self.api.get_comments_form_post(post_id)

    def get_comments(self):
        recent_posts = self.get_posts(self.post_count_for_synchronize)
        vk_comments = self.get_comments_from_post_list(recent_posts)
        comment_objects = []
        for vk_comment in vk_comments:
            comment_objects.append(Comment(vk_comment))
        return comment_objects

    def filter_comments_on_new_posts(self, comments):
        if self.clean_only_new_posts:
            comments = [comment for comment in comments
                        if comment.post_date >= self.turnedon_ts]
        return comments

    def find_trash_comments_without_filtering(self, comments_list):
        deleting_comments_list = []
        for comment in comments_list:
            lifetime = comment.sync_ts - comment.creation_ts
            if comment.likes_count < likes_function(lifetime, self.end_count,
                                                    self.end_time, self.loyal_time):
                deleting_comments_list.append(comment)
        return deleting_comments_list

    def find_trash_comments(self, comments):
        comments = self.filter_comments_on_new_posts(comments)
        return self.find_trash_comments_without_filtering(comments)

    def delete_comments(self, comments):
        comments_vkrepr = [comment.vk_representation for comment in comments]
        return self.api.delete_comments(comments_vkrepr)

    def change_disabled_status(self):
        if self.disabled is True:
            self.enable()
        else:
            self.disable()

    def disable(self):
        self.disabled = True

    def enable(self):
        self.disabled = False
        self.turnedon_ts = time.time()

    def set_queue(self, queue):
        self.queue = queue

    def acquire_token(self):
        if self.queue:
            self.access_token = self.queue.get(block=True)
        else:
            self.access_token = self.moderator.vkapp_set.all()[0].access_token

    def release_token(self):
        if self.queue:
            self.queue.put(self.access_token)
        self.queue = None
        self.access_token = ""

    def save(self):
        if self.pk is None:
            self.moderator = VkAccount.objects.all().order_by('?')[0]
            vk_group = get_group(self.domen_name)
            self.domen, self.title = vk_group["id"], vk_group["name"]
            if "photo_200" in vk_group:
                self.pic_url = vk_group["photo_200"]
            self.join()

        super().save()

    @sync
    def join(self):
        self.acquire_token()
        self.api.join()
        self.release_token()

    @sync
    def leave(self):
        self.acquire_token()
        self.api.leave()
        self.release_token()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.release_token()

    def __str__(self):
        return("%s" % (self.domen_name))


class VkApp(models.Model):
    access_token = models.CharField(max_length=300)
    account = models.ForeignKey("VkAccount")


class VkAccount(models.Model):
    url = models.CharField(max_length=300, blank=True, null=True)
    name = models.CharField(max_length=300, blank=True, null=True)

    def update_communities_moderation_statuses(self):
        access_token = self.vkapp_set.all()[0].access_token
        communities_under_moderation = get_groups_under_moderation(access_token)
        for community in self.community_set.all():
            is_under_moderation = community.domen in communities_under_moderation
            community.under_moderation = is_under_moderation
            community.save()


class Comment:
    def __init__(self, vk_comment, sync_ts=None):
        if not sync_ts:
            self.sync_ts = time.time()
        else:
            self.sync_ts = sync_ts
        self.creation_ts = vk_comment["date"]
        self.likes_count = vk_comment["likes"]["count"]
        self.vk_id = vk_comment["id"]
        self.post_date = vk_comment["post_date"]

        self.vk_representation = vk_comment

    def __repr__(self):
        return ("%s" % self.vk_id)
