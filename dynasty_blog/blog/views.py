from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render
from .models import Post
from django.views.generic import ListView


# Create your views here.
# Create class-based view for listing posts
class PostListView(ListView):
    # Alternative post list view using class-based views
    queryset = Post.published_posts.all()
    context_object_name = "posts"
    paginate_by = 3  # Show 3 posts per page
    template_name = "blog/post/list.html"

    def get_queryset(self):
        return Post.published_posts.all()


def post_list(request):
    posts_list = Post.published_posts.all()
    paginator = Paginator(posts_list, 3)  # Show 3 posts per page
    page_number = request.GET.get("page", 1)
    posts = paginator.get_page(page_number)
    # Handle empty pages
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        posts = paginator.page(paginator.num_pages)

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
