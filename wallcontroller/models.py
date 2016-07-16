from django.db import models

from vk.commands.communites import get_community_id_name


class Community(models.Model):
    url = models.CharField(max_length=300)
    moderator = models.ForeignKey("ModeratorAccount", null=True, blank=True)
    domen = models.CharField(max_length=300, null=True, blank=True)
    title = models.CharField(max_length=300, null=True, blank=True)

    def save(self):
        domen, title = get_community_id_name(self.url)
        self.domen = domen
        self.title = title
        super().save()


class ModeratorAccount(models.Model):
    access_token = models.CharField(max_length=300)


class Comment(models.Model):
    id = models.CharField(max_length=200, primary_key=True)
    start_tracking = models.DateTimeField(auto_now_add=True)
