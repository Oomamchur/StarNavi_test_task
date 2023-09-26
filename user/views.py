from django.contrib.auth import get_user_model
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import Post
from user.permissions import ReadOnly, IsCreatorOrReadOnly, IsCreatorOrIsAdmin
from user.serializers import (
    UserSerializer,
    UserListSerializer,
    UserDetailSerializer, PostSerializer, PostListSerializer, PostDetailSerializer,
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

        first_name = self.request.query_params.get("first_name")
        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)

        last_name = self.request.query_params.get("last_name")
        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)

        return queryset.distinct()


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer

        return PostListSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_permissions(self):
        if self.action in ("update", "partial_update"):
            return [IsCreatorOrReadOnly()]
        if self.action == "destroy":
            return [IsCreatorOrIsAdmin()]

        return super().get_permissions()

    # def get_queryset(self):
    #     queryset = self.queryset
    #
    #     username = self.request.query_params.get("username")
    #     if username:
    #         queryset = queryset.filter(user__username__icontains=username)
    #
    #     if self.action in ("list", "retrieve"):
    #         queryset = queryset.prefetch_related("user")
    #
    #     queryset = queryset.filter(
    #         Q(user=self.request.user)
    #         | Q(user__in=self.request.user.user_follow.all())
    #     )
    #
    #     return queryset
