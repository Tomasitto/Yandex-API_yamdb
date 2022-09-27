from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from django.contrib.auth.tokens import default_token_generator
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.v1.filters import TitlesFilter
from api.v1.viewsets import CreateListDestroyViewset
from api.v1.permissions import (
    IsAdminOrReadOnly,
    ReviewCommentOrReadOnly,
    IsAdmin
)
from reviews.models import Category, Genre, Title, Review
from users.models import User

from api.v1.serializers import (
    CommonSerializer, CategoriesSerializer,
    CommentSerializer, EmailVerifySerializer,
    GenreSerializer, ReviewSerializer, SignUpSerializer,
    TitlePostSerializer, TitleViewSerializer,
    UpdateUserSerializer
)
from api_yamdb.settings import ADMIN_EMAIL


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CommonSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    lookup_field = "username"

    @action(
        methods=["get", "patch"],
        detail=False,
        url_path="me",
        permission_classes=(IsAuthenticated,),
        serializer_class=UpdateUserSerializer,
    )
    def get_patch_me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def signup_post(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data["email"]
    username = serializer.validated_data["username"]
    user, create = User.objects.get_or_create(
        username=username, email=email
    )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        "Код подверждения",
        confirmation_code,
        [ADMIN_EMAIL],
        (email,),
        fail_silently=False,
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def token(request):
    user = request.data
    serializer = EmailVerifySerializer(data=user)
    if serializer.is_valid(raise_exception=True):
        name = serializer.validated_data["username"]
        user_info = get_object_or_404(User, username=name)
        if default_token_generator.check_token(
                user, serializer.validated_data['confirmation_code']):
            token = RefreshToken.for_user(user_info).access_token
            return Response(
                {"token": str(token)}, status=status.HTTP_200_OK
            )

        return Response({"error": "Wrong code or username"},
                        status=status.HTTP_400_BAD_REQUEST,
                        )
    return Response(
        {"error": "Serializer error"},
        status=status.HTTP_404_NOT_FOUND)


class GenreViewSet(CreateListDestroyViewset):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
    filter_backends = [filters.SearchFilter]
    search_fields = ("name",)
    lookup_field = "slug"


class CategoriesViewSet(CreateListDestroyViewset):
    serializer_class = CategoriesSerializer
    queryset = Category.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
    filter_backends = [filters.SearchFilter]
    search_fields = ("name",)
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitlesFilter

    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
            return TitleViewSerializer
        return TitlePostSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [ReviewCommentOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        return title.reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [ReviewCommentOrReadOnly]

    def get_queryset(self):
        try:
            review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        except TypeError:
            TypeError('У произведения нет такого отзыва')
        return review.comments.all()
