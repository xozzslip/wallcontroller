from django.test import TestCase
from django.contrib.auth.models import User

from .serializers import CommunitySerializer
from .models import Community

from vk.exceptions import CommunityDoesNotExist
from vk.tests import TEST_PUBLIC


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
    def test_community_creation(self):
        invalid_domen = "fsdgeroig23gv893veri32"
        community = Community(domen_name=invalid_domen, user_owner=TEST_USER)
        with self.assertRaises(CommunityDoesNotExist):
            community.save()

    def test_created_community(self):
        domen = TEST_PUBLIC.domen_name
        community = Community(domen_name=domen, user_owner=TEST_USER)
        community.save()
        self.assertTrue("http" in community.pic_url)
