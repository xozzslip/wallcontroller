from rest_framework import serializers

from .models import Community


class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = ('url', 'title', 'domen', 'domen_name', 'pic_url', 'pk')
