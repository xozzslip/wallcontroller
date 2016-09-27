import unittest
import datetime
from django.test import TestCase
from django.contrib.auth.models import User

from .serializers import CommunitySerializer
from .models import Community, VkApp, Comment
from .tasks import synchronize

from vk.exceptions import CommunityDoesNotExist
from vk.private_data import test_settings
from wallcontroller.comments_filter import to_dict, deleting_comments_list


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

    global TEST_POST_ID
    post_in_vk = TEST_COMMUNITY.api.get_post_by_text(text=test_settings.TEST_POST)
    TEST_POST_ID = post_in_vk["id"]


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
        comments = self.community.get_comments_from_post_list(posts)
        self.assertTrue(test_settings.TEST_COMMENT in str(comments))

    @classmethod
    def tearDownClass(cls):
        cls.community.delete()


class TestGettingComments(TestCase):
    def test_detecting_created_comment(self):
        """Checking that created comment will appear in db after
        synchronization

        """
        with unittest.mock.patch('default.celeryconfig.CELERY_ALWAYS_EAGER',
                                 True, create=True):
            synchronize.apply().get()
            comments = Comment.objects.filter(vk_post_id=TEST_POST_ID)
            created_comment_id = TEST_COMMUNITY.api.create_comment(
                text=test_settings.TEST_COMMENT,
                post_id=TEST_POST_ID
            )
            comments_ids = [c.vk_id for c in comments]
            self.assertFalse(created_comment_id in comments_ids)

            synchronize.apply().get()
            comments = Comment.objects.filter(vk_post_id=TEST_POST_ID)
            comments_ids = [c.vk_id for c in comments]
            self.assertTrue(created_comment_id in comments_ids)

            TEST_COMMUNITY.api.delete_comment(created_comment_id)

    def test_get_comments_in_dict(self):
        with unittest.mock.patch('default.celeryconfig.CELERY_ALWAYS_EAGER',
                                 True, create=True):
            synchronize.delay()
            synchronize.delay()
            comments_in_dict = to_dict(Comment.objects.all())
            self.assertTrue(isinstance(comments_in_dict, dict))
            self.assertTrue(len(comments_in_dict) > 0)


class TestFilteringComments(TestCase):
    @classmethod
    def setUpClass(cls):
        """
            100 — checks that likes_c = 3, than comment will be saved;
            4 — have to be deleted because of didn't get any likes for 5 hours;
            9, 33 — should be saved because of too few time has passed
            1 — has only one stamp, so shouldn't be deleted
        """
        cls.comments_dict_example = {
            100: [
                {'sync_ts': datetime.datetime(2016, 9, 27, 12, 1, 30, 562609), 'likes_c': 0, 'pk': 28},
                {'sync_ts': datetime.datetime(2016, 9, 27, 15, 1, 31, 546330), 'likes_c': 3, 'pk': 61}
            ],
            4: [
                {'sync_ts': datetime.datetime(2016, 9, 27, 12, 1, 30, 550045), 'likes_c': 1, 'pk': 3},
                {'sync_ts': datetime.datetime(2016, 9, 27, 17, 43, 1, 528903), 'likes_c': 1, 'pk': 36}
            ],
            9: [
                {'sync_ts': datetime.datetime(2016, 9, 27, 12, 1, 30, 550045), 'likes_c': 0, 'pk': 1},
                {'sync_ts': datetime.datetime(2016, 9, 27, 12, 3, 1, 528903), 'likes_c': 0, 'pk': 13}
            ],
            33: [
                {'sync_ts': datetime.datetime(2016, 9, 27, 12, 1, 15, 0), 'likes_c': 0, 'pk': 4},
                {'sync_ts': datetime.datetime(2016, 9, 27, 12, 1, 30, 0), 'likes_c': 0, 'pk': 17}
            ],
            1: [
                {'sync_ts': datetime.datetime(2016, 9, 27, 12, 1, 30, 0), 'likes_c': 0, 'pk': 5}
            ],
        }

    def test_emaple(self):
        result = deleting_comments_list(self.comments_dict_example)
        self.assertEquals(len(result), 1)
        self.assertTrue(4 in result)

    @classmethod
    def tearDownClass(cls):
        pass
