from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy
import markdown

from .models import Post


class LatestPostsFeed(Feed):
    title = "Dynasty Blog"
    link = reverse_lazy("blog:post_list")
    description = "New posts from Dynasty Blog"

    def items(self):
        # Only published posts; adjust slice if you want more
        return Post.published_posts.order_by("-published")[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        html_content = markdown.markdown(item.body)
        return truncatewords_html(html_content, 30)

    def item_link(self, item):
        # Optional (Feed will fall back to item.get_absolute_url if omitted)
        return item.get_absolute_url()

    def item_pubdate(self, item):
        # ✅ field name is 'published' on your model
        return item.published

    def item_updateddate(self, item):
        # Optional but nice for feed readers
        return item.updated_at
