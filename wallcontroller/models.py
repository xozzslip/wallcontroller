from django.db import models
from django.contrib.auth.models import User

from vk.commands import get_group


class Community(models.Model):
    url = models.CharField(max_length=300, null=True, blank=True)
    moderator = models.ForeignKey("ModeratorAccount", null=True, blank=True)
    domen = models.CharField(max_length=300, null=True, blank=True)
    domen_name = models.CharField(max_length=300)
    title = models.CharField(max_length=300, null=True, blank=True)
    pic_url = models.CharField(max_length=300, null=True, blank=True)
    user_owner = models.ForeignKey(User)

    def save(self):
        vk_group = get_group(self.domen_name)
        self.domen, self.title = vk_group["id"], vk_group["name"]
        if "photo_200" in vk_group:
            self.pic_url = vk_group["photo_200"]
        super().save()


class ModeratorAccount(models.Model):
    access_token = models.CharField(max_length=300)


class Post(models.Model):
    parent_community = models.ForeignKey("Community")
    post_id = models.CharField(max_length=300)


class Comment(models.Model):
    parent_post = models.ForeignKey("Post")
    parent_community = models.ForeignKey("Community", null=True, blank=True)
    comment_id = models.CharField(max_length=200)
    start_tracking = models.DateTimeField(auto_now_add=True)
