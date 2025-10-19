from django.shortcuts import get_object_or_404, render
from .models import Post


# Create your views here.
def post_list(request):
    posts = Post.objects.filter(status=Post.Status.PUBLISHED).order_by("-published")
    return render(request, "blog/post/list.html", {"posts": posts})


# Create a view to display a single post
def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        published__year=year,
        published__month=month,
        published__day=day,
    )

    return render(request, "blog/post/detail.html", {"post": post})
