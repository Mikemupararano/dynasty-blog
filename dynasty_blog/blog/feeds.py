import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from django.urls import reverse_lazy
from .models import Post


class LatestPostsFeed(Feed):
    title = "Dynasty Blog"
    link = reverse_lazy("blog:post_list")
    description = "New posts from Dynasty Blog"

    def items(self):
        return Post.published_posts.all()[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        html_content = markdown.markdown(item.body)
        return truncatewords_html(markdown.markdown(item.body), 30)

    def item_pubdate(self, item):
        return item.publish
