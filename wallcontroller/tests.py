from django.test import TestCase
from django.contrib.auth.models import User

from .serializers import CommunitySerializer
from .models import Community


class SerializersTestCase(TestCase):
    def setUp(self):
        self.user = User(username="kek", password="kokkokok1", email="k@k.com")

    def test_community_setializer(self):
        community = Community(url="ff", domen_name="ff", user_owner=self.user)
        serializer = CommunitySerializer(community)
        self.assertTrue(len(serializer.data) > 0)
