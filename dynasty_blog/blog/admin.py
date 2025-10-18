from django.contrib import admin
from django.utils.html import format_html
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # Add 'image_thumb' if you want a tiny preview column
    list_display = ("image_thumb", "title", "slug", "author", "published", "status")
    list_filter = ("status", "created_at", "published", "author")
    search_fields = ("title", "body", "content")
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("author",)
    date_hierarchy = "published"
    ordering = ["status", "published"]

    def image_thumb(self, obj):
        if getattr(obj, "image", None):
            return format_html(
                '<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:6px;" />',
                obj.image.url,
            )
        return "—"

    image_thumb.short_description = "Image"
    image_thumb.admin_order_field = "image"
