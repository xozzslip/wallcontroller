import unittest
from django.test import TestCase
from django.contrib.auth.models import User

from .serializers import CommunitySerializer
from .models import Community, VkApp, Comment, Post
from .tasks import synchronize

from vk.exceptions import CommunityDoesNotExist
from vk.private_data import test_settings


def setUpModule():
    global TEST_USER
    TEST_USER = User(username="kek", password="kokok1", email="k@k.com")
    TEST_USER.save()

    global TEST_APP
    TEST_APP = VkApp(access_token=test_settings.ACCESS_TOKEN)
    TEST_APP.save()

    global TEST_COMMUNITY
    TEST_COMMUNITY = Community(domen_name=test_settings.DOMEN_NAME,
                               app=TEST_APP, user_owner=TEST_USER)
    TEST_COMMUNITY.save()

    global TEST_POST
    post_in_vk = TEST_COMMUNITY.api.get_post_by_text(text=test_settings.TEST_POST)
    post_id = post_in_vk["id"]
    TEST_POST = Post(post_id=post_id, community=TEST_COMMUNITY, raw_date=0)
    TEST_POST.save()


class SerializersTestCase(TestCase):
    def test_community_setializer(self):
        community = Community(url="ff", domen_name="ff", user_owner=TEST_USER)
        serializer = CommunitySerializer(community)
        self.assertTrue(len(serializer.data) > 0)


class CommunityCreateTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.community = Community(domen_name=test_settings.DOMEN, user_owner=TEST_USER, app=TEST_APP)
        cls.community.save()

    def test_community_creation(self):
        invalid_domen = "fsdgeroig23gv893veri32"
        community = Community(domen_name=invalid_domen, user_owner=TEST_USER)
        with self.assertRaises(CommunityDoesNotExist):
            community.save()

    def test_created_community(self):
        self.assertTrue("http" in self.community.pic_url)

    def test_get_posts(self):
        COUNT = 10
        posts = self.community.get_posts(COUNT)
        self.assertEquals(len(posts), COUNT)
        self.assertTrue(test_settings.TEST_POST in str(posts))

    def test_get_comments(self):
        posts = self.community.get_posts(10)
        comments = self.community.get_comments_from_posts(posts)
        self.assertTrue(test_settings.TEST_COMMENT in str(comments))

    @classmethod
    def tearDownClass(cls):
        cls.community.delete()


class TestGettingComments(TestCase):
    def test_detecting_created_comment(self):
        """Checking that created comment will appear in db after
        synchronization
        """
        with unittest.mock.patch('default.celeryconfig.CELERY_ALWAYS_EAGER', True, create=True):
            synchronize.apply().get()
            comments = Comment.objects.filter(post__post_id=TEST_POST.post_id)
            created_comment_id = TEST_COMMUNITY.api.create_comment(
                text=test_settings.TEST_COMMENT,
                post_id=TEST_POST.post_id
            )
            print(comments)
            comments_ids = [c.comment_id for c in comments]
            self.assertFalse(created_comment_id in comments_ids)

            synchronize.apply().get()
            comments = Comment.objects.filter(post__post_id=TEST_POST.post_id)
            for c in comments:
                print(c.comment_id)
            comments_ids = [c.comment_id for c in comments]
            self.assertTrue(created_comment_id in comments_ids)

            TEST_COMMUNITY.api.delete_comment(created_comment_id)

    def test_get_comments_in_dict(self):
        with unittest.mock.patch('default.celeryconfig.CELERY_ALWAYS_EAGER', True, create=True):
            synchronize.delay()
            comments_in_dict = Comment.objects.dict()
            self.assertTrue(isinstance(comments_in_dict, dict))
            self.assertTrue(len(comments_in_dict) > 0)
