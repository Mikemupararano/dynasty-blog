from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from taggit.managers import TaggableManager


# --- Make User objects display as full name in Admin & ForeignKey widgets ---
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


@receiver(post_migrate)
def _ensure_user_str_patched(sender, **kwargs):
    _patch_user_str()


# ---------------------------------------------------------------------
# File validation helpers
# ---------------------------------------------------------------------
MAX_UPLOAD_MB = 50  # Adjust maximum upload size (in megabytes)


def validate_file_size(value):
    """Ensure uploaded file is not larger than MAX_UPLOAD_MB."""
    max_bytes = MAX_UPLOAD_MB * 1024 * 1024
    if value and value.size > max_bytes:
        raise ValidationError(f"File too large. Max size is {MAX_UPLOAD_MB} MB.")


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

    # Media fields (all optional)
    image = models.ImageField(upload_to="blog_images/", blank=True, null=True)
    audio = models.FileField(
        upload_to="blog_audio/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["mp3", "wav", "m4a", "aac", "oga", "ogg"]
            ),
            validate_file_size,
        ],
    )
    video = models.FileField(
        upload_to="blog_videos/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["mp4", "webm", "ogg", "mov", "m4v"]
            ),
            validate_file_size,
        ],
    )

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
