from django.db import models
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

    supporting_post_count = models.IntegerField(default=50)

    @property
    def api(self):
        if self.app:
            access_token = self.app.access_token
        else:
            access_token = ""
        return PublicApiCommands(access_token=access_token, domen=self.domen)

    def get_posts(self, count=None):
        if count is None:
            count = self.supporting_post_count
        return self.api.get_post_list(count)

    def get_comments_from_posts(self, posts):
        return self.api.get_comments_from_post_list(posts)

    def synchronize(self):
        recent_posts = self.get_posts()
        for post in recent_posts:
            post_object = Post(post_id=post["id"], date=post["date"], community=self)
            post_object.save()

    def save(self):
        vk_group = get_group(self.domen_name)
        self.domen, self.title = vk_group["id"], vk_group["name"]
        if "photo_200" in vk_group:
            self.pic_url = vk_group["photo_200"]
        super().save()


class VkApp(models.Model):
    access_token = models.CharField(max_length=300)


class Post(models.Model):
    community = models.ForeignKey("Community")
    post_id = models.CharField(max_length=300)
    raw_date = models.IntegerField()

    def get_comments(self):
        api = self.parent_community.api
        return api.get_comments_form_post(self.post_id)


class Comment(models.Model):
    post = models.ForeignKey("Post")
    community = models.ForeignKey("Community", null=True, blank=True)
    comment_id = models.CharField(max_length=200)
    start_tracking = models.DateTimeField(auto_now_add=True)
