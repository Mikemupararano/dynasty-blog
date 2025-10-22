from django.urls import path
from . import views
from .feeds import LatestPostsFeed

app_name = "blog"

urlpatterns = [
    # Main blog list
    path("", views.post_list, name="post_list"),
    # Tag filter route (used in list.html)
    path("tag/<slug:tag_slug>/", views.post_list, name="post_list_by_tag"),
    # Post detail
    path(
        "<int:year>/<int:month>/<int:day>/<slug:post>/",
        views.post_detail,
        name="post_detail",
    ),
    # Share via email
    path(
        "<int:post_id>/share/",
        views.post_share,
        name="post_share",
    ),
    # Comment submission
    path(
        "<int:post_id>/comment/",
        views.post_comment,
        name="post_comment",
    ),
    # RSS feed
    path("feed/", LatestPostsFeed(), name="post_feed"),
]
