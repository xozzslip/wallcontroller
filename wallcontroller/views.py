from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions


from .models import Community
from .serializers import CommunitySerializer


def communities_render(request):
    template = "wallcontroller/communities.html"
    return render(request, template)


class CommunitiesList(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request):
        own_communities = Community.objects.filter(user_owner=request.user)
        serializer = CommunitySerializer(own_communities, many=True)
        return Response(serializer.data)


class CommunitySingle(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        community = Community.objects.get(pk=pk)
        serializer = CommunitySerializer(community)
        return Response(serializer.data)
