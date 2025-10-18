from django.db import models
from django.utils import timezone


# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250)
    body = models.TextField()
    published = models.DateTimeField(default=timezone.now)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    #Present blogs in reverse chronological order, showing the most recent posts first
    class Meta:
        ordering = ['-published']
        #Adding an index on the published field to optimize queries that filter or sort by this field
        indexes = [
            models.Index(fields=['-published']),
        ]


    def __str__(self):
        return self.title
