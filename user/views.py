from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import Post, Like
from user.permissions import ReadOnly, IsCreatorOrReadOnly, IsCreatorOrIsAdmin
from user.serializers import (
    UserSerializer,
    UserListSerializer,
    UserDetailSerializer,
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer,
    LikeListSerializer,
    LikeSerializer,
)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request) -> Response:
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (ReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        if self.action == "retrieve":
            return UserDetailSerializer

        return UserSerializer

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAdminUser()]

        return super().get_permissions()

    def get_queryset(self) -> queryset:
        queryset = super().get_queryset()

        username = self.request.query_params.get("username")
        if username:
            queryset = queryset.filter(username__icontains=username)

        first_name = self.request.query_params.get("first_name")
        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)

        last_name = self.request.query_params.get("last_name")
        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="username",
                description="Filter by username (ex. ?username=user1)",
                type=str,
            ),
            OpenApiParameter(
                name="first_name",
                description="Filter by first_name (ex. ?first_name=Brad)",
                type=str,
            ),
            OpenApiParameter(
                name="last_name",
                description="Filter by last_name (ex. ?last_name=Pitt)",
                type=str,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        if self.action == "like":
            return LikeSerializer

        return PostListSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_permissions(self):
        if self.action in ("update", "partial_update"):
            return [IsCreatorOrReadOnly()]
        if self.action == "destroy":
            return [IsCreatorOrIsAdmin()]

        return super().get_permissions()

    def get_queryset(self):
        queryset = self.queryset

        username = self.request.query_params.get("username")
        if username:
            queryset = queryset.filter(user__username__icontains=username)

        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related("user")

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="username",
                description="Filter by username (ex. ?username=user1)",
                type=str,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(
        methods=["POST"],
        detail=True,
        url_path="like",
        permission_classes=(IsAuthenticated,),
    )
    def like(self, request, pk=None):
        """Endpoint for liking specific post"""
        post = self.get_object()
        user = self.request.user

        Like.objects.create(post=post, user=user, created_at=datetime.now())

        return Response(status=status.HTTP_200_OK)


class LikeList(generics.ListAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.select_related("post", "user")

        return queryset


@api_view(["GET"])
def get_likes_count_by_date(request: Request) -> Response:
    queryset = Like.objects.all()
    date_from = request.query_params.get("date_from")
    date_to = request.query_params.get("date_to")

    if date_from:
        date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
        queryset = queryset.filter(created_at__gt=date_from)

    if date_to:
        date_to = datetime.strptime(date_to, "%Y-%m-%d").date() + timedelta(
            days=1
        )
        queryset = queryset.filter(created_at__lte=date_to)

    return Response(queryset.count(), status=status.HTTP_200_OK)
