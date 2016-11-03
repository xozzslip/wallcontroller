import time
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth.models import User

from .serializers import CommunitySerializer
from .models import Community, VkApp, Comment, VkAccount
from .tasks import delete_comments

from vk.exceptions import CommunityDoesNotExist
from vk.private_data import test_settings, access_tokens


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
                               moderator=TEST_ACCOUNT, clean_only_new_posts=False)
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
            Comment({"id": 0, "post_date": 0, "likes": {"count": 1}, "date": 0}, sync_ts=10 * 3600),
            Comment({"id": 1, "post_date": 0, "likes": {"count": 1}, "date": 0}, sync_ts=0.5 * 3600),
            Comment({"id": 2, "post_date": 0, "likes": {"count": 4}, "date": 0}, sync_ts=24 * 3600),
            Comment({"id": 3, "post_date": 0, "likes": {"count": 1}, "date": 0}, sync_ts=5 * 3600),
            Comment({"id": 4, "post_date": 0, "likes": {"count": 2}, "date": 0}, sync_ts=10),
            Comment({"id": 5, "post_date": 0, "likes": {"count": 2}, "date": 0}, sync_ts=6 * 3600),
            Comment({"id": 6, "post_date": 0, "likes": {"count": 0}, "date": 0}, sync_ts=1 * 3600),
            Comment({"id": 7, "post_date": 0, "likes": {"count": 0}, "date": 0}, sync_ts=1 * 3600),
            Comment({"id": 8, "post_date": 0, "likes": {"count": 0}, "date": 0}, sync_ts=10),
        ]

    def test_sample(self):
        """ The result should be equal to
        [<Comment: {likes: 0, vk_id: 7, dtime:1.0h}>, <Comment: {likes: 0, vk_id: 6, dtime:1.0h}>,
        <Comment: {likes: 1, vk_id: 3, dtime:5.0h}>, <Comment: {likes: 1, vk_id: 0, dtime:10.0h}>]

        """
        TEST_COMMUNITY.end_count = 3
        TEST_COMMUNITY.save()
        result = TEST_COMMUNITY.find_trash_comments(self.comments)
        self.assertTrue(len(result) == 5)

    def test_empty(self):
        result = TEST_COMMUNITY.find_trash_comments([])
        self.assertTrue(len(result) == 0)

    def test_comments_on_new_and_old_posts(self):
        TEST_COMMUNITY.clean_only_new_posts = True
        comment_on_old_post = Comment({"id": 1, "post_date": time.time() - 10,
                                       "likes": {"count": 0}, "date": 0})
        TEST_COMMUNITY.turnedon_ts = time.time()
        comment_on_new_post = Comment({"id": 2, "post_date": time.time() + 10,
                                       "likes": {"count": 0}, "date": 0})

        topical_comments = TEST_COMMUNITY.filter_comments_on_new_posts(
            [comment_on_old_post]
        )
        self.assertTrue(len(topical_comments) == 0)

        topical_comments = TEST_COMMUNITY.filter_comments_on_new_posts(
            [comment_on_new_post]
        )
        self.assertTrue(len(topical_comments) == 1)

        TEST_COMMUNITY.clean_only_new_posts = False
        topical_comments = TEST_COMMUNITY.filter_comments_on_new_posts(
            [comment_on_old_post, comment_on_new_post]
        )
        self.assertTrue(len(topical_comments) == 2)

    @classmethod
    def tearDownClass(cls):
        TEST_COMMUNITY.clean_only_new_posts = False


class TestDeletingComments(TestCase):
    def test_finding_and_deleting_comments(self):
        with patch.object(TEST_COMMUNITY, 'delete_comments', return_value=[]):
            comments = TEST_COMMUNITY.get_comments()
            trash_comments = TEST_COMMUNITY.find_trash_comments(comments)
            delete_comments_list = TEST_COMMUNITY.delete_comments(trash_comments)
        self.assertTrue(len(trash_comments) >= 0)
        self.assertTrue(len(delete_comments_list) == 0)

    def test_finding_trash_comments_community_method(self):
        community_with_trash = Community(domen_name="rfpl", user_owner=TEST_USER,
                                         moderator=TEST_ACCOUNT)
        community_with_trash.save()
        community_with_trash.acquire_token()
        community_with_trash.clean_only_new_posts = True
        comments = community_with_trash.get_comments()
        community_with_trash.turnedon_ts = time.time()
        trash = community_with_trash.find_trash_comments(comments)
        self.assertTrue(len(trash) == 0)

        community_with_trash.clean_only_new_posts = False
        trash = community_with_trash.find_trash_comments(comments)
        self.assertTrue(len(trash) > 0)


class TestModels(TestCase):
    def test_moderation_statuses(self):
        TEST_COMMUNITY.under_moderation = False
        TEST_COMMUNITY.save()

        self.assertFalse(TEST_COMMUNITY.under_moderation)

        TEST_ACCOUNT.update_communities_moderation_statuses()
        new_instance_of_test_community = Community.objects.get(pk=TEST_COMMUNITY.pk)

        self.assertTrue(new_instance_of_test_community.under_moderation)

    def test_community_change_status(self):
        disabled_was = TEST_COMMUNITY.disabled
        turnedon_ts_was = TEST_COMMUNITY.turnedon_ts
        TEST_COMMUNITY.change_disabled_status()
        disabled_now = TEST_COMMUNITY.disabled
        turnedon_ts_now = TEST_COMMUNITY.turnedon_ts

        self.assertTrue(disabled_was is not disabled_now)
        self.assertTrue(turnedon_ts_now >= turnedon_ts_was)


class TestFunctionality(TestCase):
    @classmethod
    def setUpClass(cls):
        for token in access_tokens.tokens:
            vkapp = VkApp(access_token=token, account=TEST_ACCOUNT)
            vkapp.save()

        cls.communities = {
            "c1": Community(
                domen_name="131810670", user_owner=TEST_USER,
                moderator=TEST_ACCOUNT, clean_only_new_posts=True,
                end_count=0, end_time=1, loyal_time=0
            ),
            "c2": Community(
                domen_name="ef4fe", user_owner=TEST_USER,
                moderator=TEST_ACCOUNT, clean_only_new_posts=True,
                end_count=10, end_time=1, loyal_time=0
            ),
            "c3": Community(
                domen_name="132256693", user_owner=TEST_USER,
                moderator=TEST_ACCOUNT, clean_only_new_posts=True,
                end_count=10, end_time=20, loyal_time=10
            )
        }

        for c in cls.communities.values():
            c.save()
            c.acquire_token()
            c.enable()

    def test_communities(self):
        post_ids = {}
        comment_ids = {}
        for name, community in self.communities.items():
            post_ids[name] = community.create_post(test_settings.TEST_POST)
            comment_ids[name] = community.api.create_comment(
                text=test_settings.TEST_COMMENT,
                post_id=post_ids[name]
            )
        delete_comments.apply()

        new_comments_ids = {}
        for name, community in self.communities.items():
            new_comments_ids[name] = community.get_comments()

        print(new_comments_ids)
        print(comment_ids)

    @classmethod
    def tearDownClass(cls):
        pass
