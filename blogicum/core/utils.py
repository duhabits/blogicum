from blog.models import Post
from django.db.models import Count
from django.utils import timezone


def is_post_visible(post, user=None):
    if user == post.author:
        return True

    now = timezone.now()
    category_ok = post.category is None or (
        post.category.is_published and bool(post.category.slug)
    )

    return post.is_published and post.pub_date <= now and category_ok
