from django.contrib import admin
from django.utils.html import format_html

from .models import Comment, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("image_thumb", "title", "slug", "author", "published", "status")
    list_filter = ("status", "created_at", "published", "author")
    search_fields = ("title", "body", "content")
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("author",)
    date_hierarchy = "published"
    ordering = ("status", "published")

    # Optional: show filter facet counts (Django 5.1+)
    try:
        show_facets = admin.ShowFacets.ALWAYS
    except AttributeError:
        pass  # safe for older Django versions

    @admin.display(description="Image", ordering="image")
    def image_thumb(self, obj):
        img = getattr(obj, "image", None)
        if img and getattr(img, "name", ""):
            try:
                return format_html(
                    '<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:6px;" />',
                    img.url,
                )
            except Exception:
                return "—"
        return "—"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "post", "created", "active")
    list_filter = ("active", "created", "updated")
    search_fields = ("name", "email", "body")
    actions = ("approve_comments",)

    @admin.action(description="Approve selected comments")
    def approve_comments(self, request, queryset):
        queryset.update(active=True)

