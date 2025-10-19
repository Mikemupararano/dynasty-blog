from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


# Custom manager that returns only published posts
class PublishedManager(models.Manager):
    def get_queryset(self):
        # Call the parent queryset and then filter by published status
        return super().get_queryset().filter(status=self.model.Status.PUBLISHED)


class Post(models.Model):
    # Managers
    objects = models.Manager()  # Default manager
    published_posts = PublishedManager()  # Custom manager for published posts

    class Status(models.TextChoices):
        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date="published")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blog_posts",
    )
    body = models.TextField()
    image = models.ImageField(upload_to="blog_images/", blank=True, null=True)
    published = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    class Meta:
        ordering = ["-published"]
        indexes = [
            models.Index(fields=["-published"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # Use kwargs to avoid reliance on positional argument order
        return reverse(
            "blog:post_detail",
            kwargs={
                "year": self.published.year,
                "month": self.published.month,
                "day": self.published.day,
                "post": self.slug,
            },
        )
