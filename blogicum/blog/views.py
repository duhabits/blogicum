from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.http import Http404
from django.utils import timezone
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models.manager import Manager
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.core.exceptions import PermissionDenied

from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, UserEditForm
from .const import PAGINATE_BY
from core.utils import is_post_visible
from core.mixins import CommentMixinView, PostMixinView

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


class PostDetailView(DetailView):
    """Страница просмотра одного поста.

    Доступ только автору или если пост опубликован и категория опубликована.
    Отображает форму комментария (если пользователь авторизован) и список
    комментариев.
    """

    model = Post
    template_name = "blog/detail.html"
    pk_url_kwarg = "post_id"

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs["post_id"])
        if (
            not is_post_visible(post, self.request.user)
            and self.request.user != post.author
        ):
            raise Http404("Пост не доступен")
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["form"] = CommentForm()
            context["flag"] = True
        context["comments"] = self.object.comments.select_related("author")
        return context


class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            filter_published_posts(Post.objects.all())
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date')
        )


class CategoryListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = PAGINATE_BY

    def get_category(self):
        category = get_object_or_404(
            Category, is_published=True, slug=self.kwargs['category_slug']
        )
        return category

    def get_queryset(self) -> QuerySet[Any]:
        self.category = self.get_category()
        return filter_published_posts(self.category.posts)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class UserProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'page_obj'
    paginate_by = PAGINATE_BY

    def get_queryset(self) -> QuerySet[Any]:
        self.profile_user = get_object_or_404(
            User, username=self.kwargs['username']
        )
        queryset = self.profile_user.posts.all()

        # Для не-владельцев показываем только опубликованные посты
        if self.request.user != self.profile_user:
            queryset = filter_published_posts(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile_user
        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class CommentCreateView(CommentMixinView):
    fields = (('text'),)
    template_name = 'blog/comment_form.html'

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            raise PermissionDenied(
                "Вы должны войти, чтобы оставить комментарий."
            )
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)


class CommentEditUpdateView(LoginRequiredMixin, CommentMixinView):
    fields = ('text',)
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        self.comment = get_object_or_404(Comment, id=kwargs['comment_id'])

        # Проверяем авторство
        if not request.user == self.comment.author:
            raise PermissionDenied(
                "Вы не можете редактировать чужой комментарий"
            )

        return super().dispatch(request, *args, **kwargs)


class CommentDeleteDeleteView(LoginRequiredMixin, CommentMixinView):
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        self.comment = get_object_or_404(Comment, id=kwargs['comment_id'])
        if not request.user == self.comment.author:
            raise PermissionDenied("Вы не можете удалить чужой комментарий")
        return super().dispatch(request, *args, **kwargs)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostEditUpdateView(PostMixinView, UpdateView):
    pk_url_kwarg = 'post_id'


class PostDeleteDeleteView(DeleteView, PostMixinView):
    pass
