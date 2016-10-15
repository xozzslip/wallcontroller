import time
from threading import Lock
from django.db import models
from django.contrib.auth.models import User
from vk.commands import get_group
from vk.custom_api import PublicApiCommands


access_token_lock = Lock()


class Community(models.Model):
    url = models.CharField(max_length=300, null=True, blank=True)
    domen = models.CharField(max_length=300, null=True, blank=True)
    domen_name = models.CharField(max_length=300)
    title = models.CharField(max_length=300, null=True, blank=True)
    pic_url = models.CharField(max_length=300, null=True, blank=True)
    user_owner = models.ForeignKey(User)
    moderator = models.ForeignKey("VkAccount")

    post_count_for_synchronize = models.IntegerField(default=50)
    disabled = models.BooleanField(default=False)
    under_moderation = models.BooleanField(default=False)

    access_token = ""
    queue = None

    @property
    def api(self):
        return PublicApiCommands(access_token=self.access_token, domen=self.domen)

    def get_posts(self, count):
        return self.api.get_post_list(count)

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

    def delete_comments(self, comments):
        comments_vkrepr = [comment.vk_representation for comment in comments]
        return self.api.delete_comments(comments_vkrepr)

    def set_queue(self, queue):
        self.queue = queue

    def acquire_token(self):
        self.access_token = self.queue.get(block=True)

    def release_token(self):
        if not self.queue:
            assert self.access_token == ""
        if self.queue:
            self.queue.put(self.access_token)
        self.queue = None
        self.access_token = ""

    def save(self):
        if self.pk is None:
            vk_group = get_group(self.domen_name)
            self.domen, self.title = vk_group["id"], vk_group["name"]
            if "photo_200" in vk_group:
                self.pic_url = vk_group["photo_200"]

        super().save()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.release_token()


class VkApp(models.Model):
    access_token = models.CharField(max_length=300)
    account = models.ForeignKey("VkAccount")


class VkAccount(models.Model):
    url = models.CharField(max_length=300, blank=True, null=True)
    name = models.CharField(max_length=300, blank=True, null=True)


class Comment:
    def __init__(self, vk_comment, sync_ts=None):
        if not sync_ts:
            self.sync_ts = time.time()
        else:
            self.sync_ts = sync_ts
        self.creation_ts = vk_comment["date"]
        self.likes_count = vk_comment["likes"]["count"]
        self.vk_id = vk_comment["id"]

        self.vk_representation = vk_comment

    def __repr__(self):
        return ("<Comment: {likes: %s, vk_id: %s, dtime:%sh}>" % (
            self.likes_count, self.vk_id, (self.sync_ts - self.creation_ts) / 3600))
