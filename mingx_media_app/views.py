from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Post, Follow, Comment, Like, Notification, Message, Repost, Hashtag  # Ensure all models are imported
from .serializers import PostSerializer, FollowSerializer, UserSerializer, CommentSerializer, LikeSerializer, NotificationSerializer, MessageSerializer, HashtagSerializer  # Import the missing serializers
from django.contrib.auth.models import User
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count


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

        # This is Optional: Filter by keyword (search)
        keyword = request.query_params.get('keyword', None)
        if keyword:
            posts = posts.filter(content__icontains=keyword)

        # This is Optional: Filter by date range
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        if start_date and end_date:
            posts = posts.filter(created_at__range=[start_date, end_date])

        # Sorting by 'date' or 'popularity'
        sort_by = request.query_params.get('sort_by', 'date')
        if sort_by == 'popularity':  # This could be based on the number of likes or comments
            posts = posts.annotate(like_count=Count('likes')).order_by('-like_count', '-created_at')
        else:
            posts = posts.order_by('-created_at')

        paginator = PageNumberPagination()
        paginated_posts = paginator.paginate_queryset(posts, request)

        serializer = PostSerializer(paginated_posts, many=True)
        return paginator.get_paginated_response(serializer.data)


    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        # Custom endpoint to fetch the current user's information
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        post = Post.objects.get(id=request.data['post'])
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            return Response({"message": "Post already liked"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Post liked"}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        like = Like.objects.filter(user=request.user, post_id=kwargs['pk'])
        if like.exists():
            like.delete()
            return Response({"message": "Like removed"}, status=status.HTTP_200_OK)
        return Response({"message": "Like not found"}, status=status.HTTP_404_NOT_FOUND)


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(recipient=self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(Q(sender=user) | Q(recipient=user))

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)



class RepostViewSet(viewsets.ModelViewSet):
    queryset = Repost.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        original_post = Post.objects.get(id=request.data['post_id'])
        repost, created = Repost.objects.get_or_create(user=request.user, original_post=original_post)
        if not created:
            return Response({"message": "Post already reposted"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Post reposted"}, status=status.HTTP_201_CREATED)


class HashtagViewSet(viewsets.ModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        keyword = request.query_params.get('keyword', None)
        if keyword:
            hashtags = Hashtag.objects.filter(name__icontains=keyword)
        else:
            hashtags = Hashtag.objects.all()
        serializer = HashtagSerializer(hashtags, many=True)
        return Response(serializer.data)


class TrendingPostViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        # Get posts ordered by the number of likes or reposts within a given time period
        posts = Post.objects.annotate(like_count=models.Count('likes')).order_by('-like_count', '-created_at')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
