from django.db import models
from django.contrib.auth.models import User

from vk.commands import get_group_domen_and_title


class Community(models.Model):
    url = models.CharField(max_length=300)
    moderator = models.ForeignKey("ModeratorAccount", null=True, blank=True)
    domen = models.CharField(max_length=300, null=True, blank=True)
    domen_name = models.CharField(max_length=300, null=True, blank=True)
    title = models.CharField(max_length=300, null=True, blank=True)
    user_owner = models.ForeignKey(User)

    def save(self):
        domen, title = get_group_domen_and_title
        (self.domen_name)
        self.domen = domen
        self.title = title
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
