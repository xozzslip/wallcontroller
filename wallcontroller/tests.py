import unittest
from django.test import TestCase
from django.contrib.auth.models import User

from .serializers import CommunitySerializer
from .models import Community, VkApp, Comment
from .tasks import synchronize

from vk.exceptions import CommunityDoesNotExist
from vk.private_data import test_settings
from wallcontroller.comments_filter import deleting_comments_list


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


class TestFilteringFakeComments(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.comments = {
            "c1": Comment(vk_id=0, community=TEST_COMMUNITY,
                          likes_count=1, sync_ts=10 * 3600, creation_ts=0),
            "c2": Comment(vk_id=1, community=TEST_COMMUNITY,
                          likes_count=1, sync_ts=0.5 * 3600, creation_ts=0),
            "c3": Comment(vk_id=2, community=TEST_COMMUNITY,
                          likes_count=4, sync_ts=24 * 3600, creation_ts=0),
            "c4": Comment(vk_id=3, community=TEST_COMMUNITY,
                          likes_count=1, sync_ts=5 * 3600, creation_ts=0),
            "c5": Comment(vk_id=4, community=TEST_COMMUNITY,
                          likes_count=2, sync_ts=10, creation_ts=0),
            "c6": Comment(vk_id=5, community=TEST_COMMUNITY,
                          likes_count=2, sync_ts=1 * 3600, creation_ts=0),
            "c7": Comment(vk_id=6, community=TEST_COMMUNITY,
                          likes_count=0, sync_ts=1 * 3600, creation_ts=0),
            "c8": Comment(vk_id=7, community=TEST_COMMUNITY,
                          likes_count=0, sync_ts=1 * 3600, creation_ts=0),
        }
        for c in cls.comments.values():
            c.save()

    def test_sample(self):
        """ The result should be equal to
        [<Comment: {likes: 0, vk_id: 7, dtime:1.0h}>, <Comment: {likes: 0, vk_id: 6, dtime:1.0h}>,
        <Comment: {likes: 1, vk_id: 3, dtime:5.0h}>, <Comment: {likes: 1, vk_id: 0, dtime:10.0h}>]

        """
        result = deleting_comments_list(Comment.objects.all())
        self.assertTrue(len(result) == 4)

    def test_empty(self):
        result = deleting_comments_list([])
        self.assertTrue(len(result) == 0)

    @classmethod
    def tearDownClass(cls):
        for c in cls.comments.values():
            c.delete()


class TestFilteringCommentsInGroups(TestCase):
    pass
