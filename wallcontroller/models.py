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

    def synchronize(self):
        recent_posts = self.get_posts(self.post_count_for_synchronize)
        for post in recent_posts:
            post = Post(post_id=post["id"], raw_date=post["date"], community=self)
            post.save()
        comments = self.get_comments_from_post_list(recent_posts)
        for comment in comments:
            comment = Comment(community=self, post_id=comment["post_id"],
                              comment_id=comment["id"],
                              likes_count=comment["likes"]["count"])
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


class Post(models.Model):
    community = models.ForeignKey("Community")
    post_id = models.IntegerField()
    raw_date = models.IntegerField()

    def get_comments(self):
        api = self.parent_community.api
        return api.get_comments_form_post(self.post_id)


class CommentManager(models.Manager):
    def dict(self):
        qs = super().get_queryset().all()
        result_dict = {comment.comment_id: [] for comment in qs}
        for comment in qs:
            comment_info = {
                "time": comment.start_tracking,
                "likes_count": comment.likes_count,
                "pk": comment.pk
            }
            result_dict[comment.comment_id].append(comment_info)
        return result_dict


class Comment(models.Model):
    post_id = models.IntegerField()
    community = models.ForeignKey("Community", null=True, blank=True)
    comment_id = models.IntegerField()
    start_tracking = models.DateTimeField(auto_now_add=True)
    likes_count = models.IntegerField(default=0)

    objects = CommentManager()
