from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Post, Follow
from .serializers import PostSerializer, FollowSerializer
from django.contrib.auth.models import User
from django.http import Http404


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            # Ensure the 'following' user exists
            following = User.objects.get(username=request.data['following'])
        except User.DoesNotExist:
            raise Http404("User not found")

        # Create the follow relationship if not already existing
        follow, created = Follow.objects.get_or_create(follower=request.user, following=following)
        if created:
            return Response(FollowSerializer(follow).data)
        else:
            return Response({"message": "Already following this user"})

    def destroy(self, request, *args, **kwargs):
        try:
            # Ensure the user to be unfollowed exists
            following = User.objects.get(username=kwargs['pk'])
        except User.DoesNotExist:
            raise Http404("User not found")

        # Remove the follow relationship
        Follow.objects.filter(follower=request.user, following=following).delete()
        return Response({"message": "Unfollowed the user"})
