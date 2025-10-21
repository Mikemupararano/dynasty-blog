# blog/templatetags/blog_tags.py
from django import template
from blog.models import Post

register = template.Library()


@register.simple_tag
def total_posts():
    """Returns the total number of published blog posts."""
    return Post.published_posts.count()


@register.inclusion_tag("blog/post/latest_posts.html")
def show_latest_posts(count=5):
    """Returns the latest published blog posts."""

    latest_posts = Post.published_posts.order_by("-published")[:count]
    return {"latest_posts": latest_posts}
