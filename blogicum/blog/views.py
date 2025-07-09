from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models.manager import Manager

from .models import Post, Category
from .const import MAX_POSTS_LIMIT


def filter_published_posts(queryset: Manager):
    return queryset.select_related(
        'category',
        'location',
        'author',
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )


def index(request):
    posts = filter_published_posts(Post.objects)[:MAX_POSTS_LIMIT]
    return render(request, 'blog/index.html', {'post_list': posts})


def post_detail(request, post_id):
    post = get_object_or_404(filter_published_posts(Post.objects), pk=post_id)
    return render(request, 'blog/detail.html', {'post': post})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category, is_published=True, slug=category_slug
    )
    posts = filter_published_posts(category.posts)
    return render(
        request,
        'blog/category.html',
        {
            'post_list': posts,
            'category': category,
        },
    )
