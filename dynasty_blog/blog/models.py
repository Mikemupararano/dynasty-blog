from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager


# --- Make User objects display as full name in Admin & ForeignKey widgets ---
# We try to patch immediately; if the app registry isn't ready yet, we also
# patch after migrations using a signal as a fallback.
def _patch_user_str():
    try:
        from django.contrib.auth import get_user_model

        User = get_user_model()
        if not getattr(User, "_str_patched_for_full_name", False):

            def _user_str(self):
                full = (self.get_full_name() or "").strip()
                return full if full else self.get_username()

            User.__str__ = _user_str
            User._str_patched_for_full_name = True
    except Exception:
        # If this runs too early (e.g., during app loading), we'll patch later
        pass


_patch_user_str()

# Fallback: ensure the patch exists after migrations when apps are fully ready
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def _ensure_user_str_patched(sender, **kwargs):
    _patch_user_str()


# ---------------------------------------------------------------------
# Custom Manager for Published Posts
# ---------------------------------------------------------------------
class PublishedManager(models.Manager):
    """Custom manager that returns only posts with Published status."""

    def get_queryset(self):
        return super().get_queryset().filter(status=self.model.Status.PUBLISHED)


# ---------------------------------------------------------------------
# Post Model
# ---------------------------------------------------------------------
class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"

    # Core fields
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date="published")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blog_posts",
    )
    body = models.TextField()
    image = models.ImageField(upload_to="blog_images/", blank=True, null=True)

    # Date fields
    published = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Status field
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    # Managers
    objects = models.Manager()  # Default manager
    published_posts = PublishedManager()  # Custom manager for published posts

    # Tags
    tags = TaggableManager()

    class Meta:
        ordering = ["-published"]
        indexes = [
            models.Index(fields=["-published"]),
        ]
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.title

    @property
    def author_display(self) -> str:
        """
        Prefer the author's full name; fall back to a prettified username.
        Useful for templates and admin list displays.
        """
        user = self.author
        full = (user.get_full_name() or "").strip()
        if full:
            return full
        # Graceful fallback: "mike_thomas" / "mike.thomas" -> "Mike Thomas"
        uname = (
            (getattr(user, "username", "") or "").replace("_", " ").replace(".", " ")
        )
        pretty = uname.title().strip()
        return pretty or user.get_username()

    def get_absolute_url(self):
        """Return canonical URL for a post."""
        return reverse(
            "blog:post_detail",
            kwargs={
                "year": self.published.year,
                "month": self.published.month,
                "day": self.published.day,
                "post": self.slug,
            },
        )


# ---------------------------------------------------------------------
# Comment Model
# ---------------------------------------------------------------------
class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["created"]
        indexes = [
            models.Index(fields=["created"]),
        ]
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"
