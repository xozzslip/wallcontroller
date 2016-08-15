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

    @property
    def api(self):
        if self.app:
            access_token = self.app.access_token
        else:
            access_token = ""
        return PublicApiCommands(access_token=access_token, domen=self.domen)

    def posts(self, count):
        return self.api.get_post_list(count)

    def comments(self, post_list):
        return self.api.get_comments_from_post_list(post_list)

    def save(self):
        vk_group = get_group(self.domen_name)
        self.domen, self.title = vk_group["id"], vk_group["name"]
        if "photo_200" in vk_group:
            self.pic_url = vk_group["photo_200"]
        super().save()


class VkApp(models.Model):
    access_token = models.CharField(max_length=300)


class Post(models.Model):
    parent_community = models.ForeignKey("Community")
    post_id = models.CharField(max_length=300)


class Comment(models.Model):
    parent_post = models.ForeignKey("Post")
    parent_community = models.ForeignKey("Community", null=True, blank=True)
    comment_id = models.CharField(max_length=200)
    start_tracking = models.DateTimeField(auto_now_add=True)
