import unittest

from .vkapi import VkApi
from .custom_api import PublicApiCommands
from .exceptions import VkApiError
from .commands import get_group, get_group_domen, get_group_domen_and_title


class Public:
    def __init__(self, url, domen_name, domen):
        self.url = url
        self.domen_name = domen_name
        self.domen = domen


TEST_PUBLIC = Public(
    url="https://new.vk.com/khasanlab",
    domen_name="khasanlab",
    domen=87470452
)

BIG_PUBLIC = Public(
    url="https://new.vk.com/40kg",
    domen_name="40kg",
    domen=28627911
)


class TestComplexRequests(unittest.TestCase):
    def setUp(self):
        self.connection = VkApi(access_token="", v="5.52")

    def test_get_posts(self):
        params = "owner_id=-%s" % TEST_PUBLIC.domen
        items = self.connection.complex_request("wall.get", params, 1)
        self.assertEqual(len(items), 1)
        items = self.connection.complex_request("wall.get", params, 10)
        self.assertEqual(len(items), 10)

    def test_groupsgetById_explicit(self):
        """
        count of items id specified explicity
        """
        params = "group_id=%s" % TEST_PUBLIC.domen_name
        items = self.connection.complex_request("groups.getById", params, 1)
        group = items[0]
        self.assertEqual(group["id"], TEST_PUBLIC.domen)

    def test_groupsgetById_implicit(self):
        params = "group_id=%s" % TEST_PUBLIC.domen_name
        items = self.connection.complex_request("groups.getById", params)
        group = items[0]
        self.assertEqual(group["id"], TEST_PUBLIC.domen)

    def test_request_with_error(self):
        params = "group_id=%s" % "group_that_doesnot_exists123321"
        with self.assertRaises(VkApiError) as er:
            self.connection.complex_request("groups.getById", params)
        self.assertEqual(er.exception.code, 100)


class TestPublicApiCommands(unittest.TestCase):
    def setUp(self):
        self.public = PublicApiCommands(access_token="", v="5.52",
                                        domen=TEST_PUBLIC.domen)

    def test_get_group_domen_in_apicontext(self):
        self.assertEqual(self.public.domen, TEST_PUBLIC.domen)

    def test_get_post_list(self):
        """
        count < MAX_PER_REQ
        """
        items = self.public.get_post_list(10)
        self.assertEqual(len(items), 10)

    def test_get_post_list_big_pub(self):
        BIG_PUBLIC_api = PublicApiCommands(access_token="", v="5.52",
                                           domen=BIG_PUBLIC.domen)

        items = BIG_PUBLIC_api.get_post_list(300)
        self.assertEqual(len(items), 300)

    def test_get_comments_form_post(self):
        posts = self.public.get_post_list(count=1)
        post = posts[0]
        comments = self.public.get_comments_form_post(post)
        self.assertIsInstance(comments, list)

    def test_get_comments_from_post_list(self):
        posts = self.public.get_post_list(count=15)
        comments = self.public.get_comments_from_post_list(posts)
        self.assertTrue(len(comments) > 0)
        self.assertTrue("likes" in comments[0])


class TestCommands(unittest.TestCase):
    def test_get_group_domen(self):
        domen_name = TEST_PUBLIC.domen_name
        domen = get_group_domen(domen_name)
        self.assertEqual(domen, TEST_PUBLIC.domen)

    def test_get_group_domen_and_title(self):
        domen_name = TEST_PUBLIC.domen_name
        domen, title = get_group_domen_and_title(domen_name)
        self.assertEqual(domen, TEST_PUBLIC.domen)

    def test_get_invalid_group(self):
        domen_name = "invalid_domen_name_123_123_321_321"
        with self.assertRaises(VkApiError) as er:
            get_group(domen_name)
        self.assertEqual(er.exception.code, 100)


if __name__ == '__main__':
    unittest.main()
