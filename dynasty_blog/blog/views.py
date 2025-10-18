from django.shortcuts import render
from .models import Post


# Create your views here.
def post_list(request):
    posts = Post.published.all()
    return render(request, "blog/post/list.html", {"posts": posts})


# Create a view to display a single post
def post_detail(request, id):
    try:
        post = Post.published.get(id=id)
    except Post.DoesNotExist:
        raise Http404("No Post found.")
    return render(request, "blog/post/detail.html", {"post": post})
