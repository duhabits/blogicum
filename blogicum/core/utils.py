from django.utils import timezone
from django.db.models import Count


def annotate_with_comment_count(queryset):
    return (
        queryset.annotate(comment_count=Count("comments"))
        .order_by('-pub_date')
        .select_related("category")
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
