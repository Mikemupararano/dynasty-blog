# blog/views.py

from django.conf import settings
from django.contrib import messages
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.mail import EmailMessage, send_mail
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from taggit.models import Tag

from .forms import EmailPostForm, CommentForm, SearchForm, ContactForm
from .models import Post


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
                return redirect(reverse("blog:post_share", args=[post.id]) + "?sent=1")
            except Exception as e:
                messages.error(request, f"Could not send email: {e}")
    else:
        form = EmailPostForm()
        if request.GET.get("sent"):
            sent = True

    return render(
        request, "blog/post/share.html", {"post": post, "form": form, "sent": sent}
    )


class PostListView(ListView):
    queryset = Post.published_posts.all()
    context_object_name = "posts"
    paginate_by = 3
    template_name = "blog/post/list.html"


def post_list(request, tag_slug=None):
    """Function-based post list (your urls.py expects this name)."""
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

    comments = post.comments.filter(active=True)
    form = CommentForm()

    post_tag_ids = list(post.tags.values_list("id", flat=True))
    if post_tag_ids:
        similar_posts = (
            Post.published_posts.filter(tags__in=post_tag_ids)
            .exclude(id=post.id)
            .annotate(same_tags=Count("tags", distinct=True))
            .order_by("-same_tags", "-published")
            .distinct()[:4]
        )
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


def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if "query" in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data["query"]

            if connection.vendor == "postgresql":
                search_vector = SearchVector("title", weight="A") + SearchVector(
                    "body", weight="B"
                )
                search_query = SearchQuery(query)
                results = (
                    Post.published_posts.annotate(
                        search=search_vector,
                        rank=SearchRank(search_vector, search_query),
                    )
                    .filter(rank__gte=0.3)
                    .order_by("-rank", "-published")
                )
            else:
                results = (
                    (
                        Post.published_posts.filter(title__icontains=query)
                        | Post.published_posts.filter(body__icontains=query)
                    )
                    .distinct()
                    .order_by("-published")
                )

    return render(
        request,
        "blog/post/search.html",
        {"form": form, "query": query, "results": results},
    )


# ---------- STATIC PAGES ----------
def about(request):
    return render(request, "blog/about.html")


def contact(request):
    """
    Single contact endpoint (GET + POST).
    Sends the message to your inbox and sets Reply-To to the sender,
    so clicking Reply emails the person who filled the form.
    """
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            sender_email = form.cleaned_data["email"]
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]

            # Where contact form messages should go (your inbox).
            # Prefer CONTACT_EMAIL if you set it, otherwise fall back to EMAIL_HOST_USER.
            to_email = (
                getattr(settings, "CONTACT_EMAIL", None) or settings.EMAIL_HOST_USER
            )

            # Send FROM your authenticated sender (Gmail), but set Reply-To to the visitor.
            email = EmailMessage(
                subject=f"[Ndikiye Family Blog] {subject}",
                body=f"From: {name} <{sender_email}>\n\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[to_email],
                reply_to=[sender_email],
            )
            email.send(fail_silently=False)

            messages.success(request, "Thanks! Your message has been sent.")
            return redirect(
                "blog:contact"
            )  # PRG pattern: prevents double-send on refresh

        messages.error(request, "Please fix the errors below.")
    else:
        form = ContactForm()

    return render(request, "blog/contact.html", {"form": form})
