from django.test import TestCase
from django.contrib.auth.models import User

from .serializers import CommunitySerializer
from .models import Community

from vk.exceptions import CommunityDoesNotExist
from vk.tests import TEST_PUBLIC, TEST_COMMENT, TEST_POST


def setUpModule():
    global TEST_USER
    TEST_USER = User(username="kek", password="kokok1", email="k@k.com")
    TEST_USER.save()


class SerializersTestCase(TestCase):
    def test_community_setializer(self):
        community = Community(url="ff", domen_name="ff", user_owner=TEST_USER)
        serializer = CommunitySerializer(community)
        self.assertTrue(len(serializer.data) > 0)


class CommunityCreateTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.community = Community(domen_name=TEST_PUBLIC.domen, user_owner=TEST_USER)
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
        self.assertTrue(TEST_POST in str(posts))

    def test_get_comments(self):
        posts = self.community.get_posts(10)
        comments = self.community.get_comments_from_posts(posts)
        self.assertTrue(TEST_COMMENT in str(comments))

    def test_synchronize(self):
        pass

    @classmethod
    def tearDownClass(cls):
        cls.community.delete()
