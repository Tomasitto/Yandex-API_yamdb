from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.views import (CategoriesViewSet, CommentViewSet,
                          GenreViewSet, ReviewViewSet,
                          TitleViewSet, UserViewSet,
                          signup_post, token)

app_name = "api"

router_v1 = DefaultRouter()
router_v1.register("users", UserViewSet, basename='users')
router_v1.register("titles", TitleViewSet, basename="titles")
router_v1.register("genres", GenreViewSet, basename="genres")
router_v1.register("categories", CategoriesViewSet, basename="categories")
router_v1.register(
    r"titles/(?P<title_id>[\d]+)/reviews", ReviewViewSet, basename="reviews"
)

router_v1.register(
    r"titles/(?P<title_id>[\d]+)/reviews/(?P<review_id>[\d]+)/comments",
    CommentViewSet,
    basename="comments",
)
urlpatterns_auth = [path("auth/signup/", signup_post),
                    path("auth/token/", token)]

urlpatterns = [
    path("v1/", include(urlpatterns_auth)),
    path("v1/", include(router_v1.urls)),
]
