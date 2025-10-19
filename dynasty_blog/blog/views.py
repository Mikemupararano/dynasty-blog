from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from .models import Post


# Create your views here.
def post_list(request):
    posts_list = Post.published.all()
    paginator = Paginator(posts_list, 3)  # Show 3 posts per page
    page_number = request.GET.get("page", 1)
    posts = paginator.get_page(page_number)
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
