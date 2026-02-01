# blog/templatetags/blog_tags.py
from django import template
from blog.models import Post
from django.db.models import Count
import markdown
from django.utils.safestring import mark_safe

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


# Creating a template tag that returns a Queryset
@register.simple_tag
def get_most_commented_posts(count=5):
    """Returns the most commented published blog posts."""
    return Post.published_posts.annotate(total_comments=Count("comments")).order_by(
        "-total_comments"
    )[:count]


@register.filter(name="markdown")
def markdown_format(text):
    """Converts Markdown text to HTML."""
    return mark_safe(markdown.markdown(text))
