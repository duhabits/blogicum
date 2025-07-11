from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models.manager import Manager
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from .models import Post, Category, Comment
from .const import MAX_POSTS_LIMIT
from .forms import CongratulationForm

User = get_user_model()


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


def post_detail(request, post_id):
    post = get_object_or_404(filter_published_posts(Post.objects), pk=post_id)
    return render(
        request,
        'blog/detail.html',
        {'post': post, 'form': CongratulationForm()},
    )


class IndexListView(ListView, LoginRequiredMixin):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10


class СategoryListView(ListView, LoginRequiredMixin):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        self.category = get_object_or_404(
            Category, is_published=True, slug=self.kwargs['category_slug']
        )
        return filter_published_posts(self.category.posts)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class UserProfileView(ListView, LoginRequiredMixin):
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'page_obj'
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        user = get_object_or_404(User, username=self.kwargs['username'])
        return user.posts.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs['username']
        )
        return context


class CommentCreateView(CreateView, LoginRequiredMixin):
    model = Comment
    fields = (('text'),)
    template_name = 'blog/comment_form.html'

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )
