from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Post, Follow
from .serializers import PostSerializer, FollowSerializer, UserSerializer
from django.contrib.auth.models import User
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db.models import Q


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return Response({"error": "You can only update your own posts"}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return Response({"error": "You can only delete your own posts"}, status=403)
        return super().destroy(request, *args, **kwargs)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            # Ensure the 'following' user exists
            following = User.objects.get(username=request.data['following'])
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Prevent users from following themselves
        if request.user == following:
            return Response({"error": "You cannot follow yourself"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the follow relationship if not already existing
        follow, created = Follow.objects.get_or_create(follower=request.user, following=following)
        if created:
            return Response(FollowSerializer(follow).data)
        else:
            return Response({"message": "Already following this user"}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        try:
            # Ensure the user to be unfollowed exists
            following = User.objects.get(username=kwargs['pk'])
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Remove the follow relationship
        Follow.objects.filter(follower=request.user, following=following).delete()
        return Response({"message": "Unfollowed the user"}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only allow users to see their own information
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        # Creating a new user (could use a public endpoint with custom permissions)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        if user != request.user:
            return Response({"error": "You can only update your own profile"}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user != request.user:
            return Response({"error": "You can only delete your own profile"}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

class FeedViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        user = request.user
        # Get all users the current user is following
        followed_users = Follow.objects.filter(follower=user).values_list('following', flat=True)

        # Filter posts by followed users
        posts = Post.objects.filter(author__in=followed_users).order_by('-created_at')

        # Optional: Filter by keyword (search)
        keyword = request.query_params.get('keyword', None)
        if keyword:
            posts = posts.filter(content__icontains=keyword)

        # Optional: Filter by date range
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        if start_date and end_date:
            posts = posts.filter(created_at__range=[start_date, end_date])

        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        # Custom endpoint to fetch the current user's information
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)