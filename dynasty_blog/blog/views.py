from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView
from django.views.decorators.http import require_POST
from django.db.models import Count
from taggit.models import Tag

from .forms import EmailPostForm, CommentForm
from .models import Post, Comment


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} ({cd['email']}) recommends you read {post.title}"
            message = (
                f"Read “{post.title}” at {post_url}\n\n"
                f"{cd['name']}'s comments:\n{cd['comments']}"
            )

            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[cd["to"]],
                    fail_silently=False,
                )
                messages.success(request, "Email sent successfully.")
                sent = True
                # PRG pattern to prevent form resubmission
                return redirect(reverse("blog:post_share", args=[post.id]) + "?sent=1")
            except Exception as e:
                messages.error(request, f"Could not send email: {e}")
    else:
        form = EmailPostForm()
        if request.GET.get("sent"):
            sent = True

    return render(
        request,
        "blog/post/share.html",
        {"post": post, "form": form, "sent": sent},
    )


class PostListView(ListView):
    queryset = Post.published_posts.all()
    context_object_name = "posts"
    paginate_by = 3
    template_name = "blog/post/list.html"


def post_list(request, tag_slug=None):
    posts_list = Post.published_posts.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts_list = posts_list.filter(tags__in=[tag])
    paginator = Paginator(posts_list, 3)
    page_number = request.GET.get("page", 1)
    posts = paginator.get_page(page_number)
    return render(request, "blog/post/list.html", {"posts": posts, "tag": tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        published__year=year,
        published__month=month,
        published__day=day,
    )

    # List of active comments for this post
    comments = post.comments.filter(active=True)

    # Form for users to add comments
    form = CommentForm()

    # List of similar posts
    post_tag_ids = list(post.tags.values_list("id", flat=True))
    if post_tag_ids:
        similar_posts = (
            Post.published_posts.filter(tags__in=post_tag_ids)
            .exclude(id=post.id)
            .annotate(same_tags=Count("tags", distinct=True))
            .order_by("-same_tags", "-published")
            .distinct()
        )[:4]
    else:
        similar_posts = []

    return render(
        request,
        "blog/post/detail.html",
        {
            "post": post,
            "comments": comments,
            "form": form,
            "similar_posts": similar_posts,
        },
    )


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
        messages.success(request, "Your comment has been submitted successfully.")
    else:
        messages.error(request, "Please correct the errors below.")
    return render(
        request,
        "blog/post/comment.html",
        {"post": post, "form": form, "comment": comment},
    )
