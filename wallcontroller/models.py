import time
from django.db import models, transaction
from django.contrib.auth.models import User

from vk.commands import get_group
from vk.custom_api import PublicApiCommands


class Community(models.Model):
    url = models.CharField(max_length=300, null=True, blank=True)
    app = models.ForeignKey("VkApp", null=True, blank=True)
    domen = models.CharField(max_length=300, null=True, blank=True)
    domen_name = models.CharField(max_length=300)
    title = models.CharField(max_length=300, null=True, blank=True)
    pic_url = models.CharField(max_length=300, null=True, blank=True)
    user_owner = models.ForeignKey(User)

    post_count_for_synchronize = models.IntegerField(default=50)
    disabled = models.BooleanField(default=False)

    @property
    def api(self):
        if self.app:
            access_token = self.app.access_token
        else:
            access_token = ""
        return PublicApiCommands(access_token=access_token, domen=self.domen)

    def get_posts(self, count):
        return self.api.get_post_list(count)

    def get_comments_from_post_list(self, posts):
        return self.api.get_comments_from_post_list(posts)

    def get_comments_form_post(self, post_id):
        return self.api.get_comments_form_post(post_id)

    @transaction.atomic
    def synchronize(self):
        recent_posts = self.get_posts(self.post_count_for_synchronize)
        vk_comments = self.get_comments_from_post_list(recent_posts)
        for vk_comment in vk_comments:
            try:
                comment = Comment.objects.get(community=self, vk_id=vk_comment["id"])
            except Comment.DoesNotExist:
                comment = Comment(community=self, vk_id=vk_comment["id"],
                                  creation_ts=vk_comment["date"], vk_post_id=vk_comment["post_id"])
            comment.likes_count = vk_comment["likes"]["count"]
            comment.sync_ts = time.time()
            comment.save()

    def save(self):
        vk_group = get_group(self.domen_name)
        self.domen, self.title = vk_group["id"], vk_group["name"]
        if "photo_200" in vk_group:
            self.pic_url = vk_group["photo_200"]
        if not self.app:
            self.app = VkApp.objects.all().order_by('?')[0]
        super().save()


class VkApp(models.Model):
    access_token = models.CharField(max_length=300)


class Comment(models.Model):
    vk_post_id = models.IntegerField(default=0)
    community = models.ForeignKey("Community", null=True, blank=True)
    vk_id = models.IntegerField()
    likes_count = models.IntegerField(default=0)
    sync_ts = models.FloatField(default=0)
    creation_ts = models.FloatField(default=0)

    class Meta:
        unique_together = (("community", "vk_id"),)

    def __repr__(self):
        return ("<Comment: {likes: %s, vk_id: %s, dtime:%sh}>" % (
            self.likes_count, self.vk_id, (self.sync_ts - self.creation_ts) / 3600))
