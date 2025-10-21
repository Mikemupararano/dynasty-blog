from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView
from django.views.decorators.http import require_POST
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
                # Option A: simple plaintext
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,  # or None to use default
                    recipient_list=[cd["to"]],
                    fail_silently=False,
                )

                # Option B: richer control (reply-to)
                # email = EmailMessage(
                #     subject=subject,
                #     body=message,
                #     from_email=settings.DEFAULT_FROM_EMAIL,
                #     to=[cd["to"]],
                #     reply_to=[cd["email"]],  # so recipient can reply to the recommender
                # )
                # email.send(fail_silently=False)

                messages.success(request, "Email sent successfully.")
                sent = True
                # PRG: redirect to avoid resubmission on refresh
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
    # def get_queryset(self):  # not needed because queryset is already set
    #     return Post.published_posts.all()


def post_list(request):
    posts_list = Post.published_posts.all()
    paginator = Paginator(posts_list, 3)
    page_number = request.GET.get("page", 1)
    # get_page() safely handles non-integer and out-of-range pages
    posts = paginator.get_page(page_number)
    return render(request, "blog/post/list.html", {"posts": posts})


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

    return render(
        request,
        "blog/post/detail.html",
        {"post": post, "comments": comments, "form": form},
    )


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a comment object but don't save to database yet
        comment = form.save(commit=False)
        # Assign the current post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()
    return render(
        request,
        "blog/post/comment.html",
        {"post": post, "form": form, "comment": comment},
    )
