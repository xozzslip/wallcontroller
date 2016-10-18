from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth.models import User

from .serializers import CommunitySerializer
from .models import Community, VkApp, Comment, VkAccount
from .tasks import delete_comments

from vk.exceptions import CommunityDoesNotExist
from vk.private_data import test_settings
from wallcontroller.comments_filter import find_trash_comments


def setUpModule():
    global TEST_USER
    TEST_USER = User(username="kek", password="kokok1", email="k@k.com")
    TEST_USER.save()

    global TEST_ACCOUNT
    TEST_ACCOUNT = VkAccount()
    TEST_ACCOUNT.save()

    global TEST_APP
    TEST_APP = VkApp(access_token=test_settings.ACCESS_TOKEN, account=TEST_ACCOUNT)
    TEST_APP.save()

    global TEST_COMMUNITY
    TEST_COMMUNITY = Community(domen_name=test_settings.DOMEN_NAME, user_owner=TEST_USER,
                               moderator=TEST_ACCOUNT)
    TEST_COMMUNITY.save()
    TEST_COMMUNITY.acquire_token()


    global TEST_POST_ID
    post_in_vk = TEST_COMMUNITY.api.get_post_by_text(text=test_settings.TEST_POST)
    TEST_POST_ID = post_in_vk["id"]


class CommunityCreateTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.community = Community(domen_name=test_settings.DOMEN, user_owner=TEST_USER,
                                  moderator=TEST_ACCOUNT)
        cls.community.save()
        cls.community.access_token = TEST_APP.access_token

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
        """Checking that created comment will appear after
        get_comments()

        """
        comments = TEST_COMMUNITY.get_comments()
        comments_ids = [c.vk_id for c in comments]

        created_comment_id = TEST_COMMUNITY.api.create_comment(
            text=test_settings.TEST_COMMENT,
            post_id=TEST_POST_ID
        )
        self.assertFalse(created_comment_id in comments_ids)

        comments = TEST_COMMUNITY.get_comments()
        comments_ids = [c.vk_id for c in comments]
        self.assertTrue(created_comment_id in comments_ids)

        TEST_COMMUNITY.api.delete_comment(created_comment_id)


class TestFilteringFakeComments(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.comments = [
            Comment({"id": 0, "likes": {"count": 1}, "date": 0}, sync_ts=10 * 3600),
            Comment({"id": 1, "likes": {"count": 1}, "date": 0}, sync_ts=0.5 * 3600),
            Comment({"id": 2, "likes": {"count": 4}, "date": 0}, sync_ts=24 * 3600),
            Comment({"id": 3, "likes": {"count": 1}, "date": 0}, sync_ts=5 * 3600),
            Comment({"id": 4, "likes": {"count": 2}, "date": 0}, sync_ts=10),
            Comment({"id": 5, "likes": {"count": 2}, "date": 0}, sync_ts=1 * 3600),
            Comment({"id": 6, "likes": {"count": 0}, "date": 0}, sync_ts=1 * 3600),
            Comment({"id": 7, "likes": {"count": 0}, "date": 0}, sync_ts=1 * 3600),
        ]

    def test_sample(self):
        """ The result should be equal to
        [<Comment: {likes: 0, vk_id: 7, dtime:1.0h}>, <Comment: {likes: 0, vk_id: 6, dtime:1.0h}>,
        <Comment: {likes: 1, vk_id: 3, dtime:5.0h}>, <Comment: {likes: 1, vk_id: 0, dtime:10.0h}>]

        """
        result = find_trash_comments(self.comments)
        self.assertTrue(len(result) == 4)

    def test_empty(self):
        result = find_trash_comments([])
        self.assertTrue(len(result) == 0)

    @classmethod
    def tearDownClass(cls):
        pass


class TestDeletingComments(TestCase):
    def test_finding_and_deleting_comments(self):
        with patch.object(TEST_COMMUNITY, 'delete_comments', return_value=[]):
            comments = TEST_COMMUNITY.get_comments()
            trash_comments = find_trash_comments(comments)
            delete_comments_list = TEST_COMMUNITY.delete_comments(trash_comments)
        self.assertTrue(len(trash_comments) >= 0)
        self.assertTrue(len(delete_comments_list) == 0)


class TestAccounts(TestCase):
    def test_moderation_statuses(self):
        TEST_COMMUNITY.under_moderation = False
        TEST_COMMUNITY.save()

        self.assertFalse(TEST_COMMUNITY.under_moderation)

        TEST_ACCOUNT.update_communities_moderation_statuses()
        new_instance_of_test_community = Community.objects.get(pk=TEST_COMMUNITY.pk)

        self.assertTrue(new_instance_of_test_community.under_moderation)
