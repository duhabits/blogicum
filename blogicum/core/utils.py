from django.utils import timezone
from django.db.models import Count


def is_post_visible(post, user=None):
    if user == post.author:
        return True

    now = timezone.now()
    category_ok = post.category is None or (
        post.category.is_published and bool(post.category.slug)
    )

    return post.is_published and post.pub_date <= now and category_ok


def annotate_with_comment_count(queryset):
    return queryset.annotate(comment_count=Count("comments")).order_by(
        '-pub_date'
    )


def filter_published_posts(queryset):
    return queryset.select_related(
        'category',
        'location',
        'author',
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )
