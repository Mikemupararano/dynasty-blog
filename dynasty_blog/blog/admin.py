from django.contrib import admin
from .models import Post

admin.site.register(Post)


# Register your models here.
# Customise how models are displayed.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "author", "published", "status")
    list_filter = ("status", "created_at", "published", "author")
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("author",)
    date_hierarchy = "published"
    ordering = ["status", "published"]
