from typing import Any
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models.manager import Manager
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.core.exceptions import PermissionDenied

from .models import Post, Category, Comment
from .forms import PostForm, CongratulationForm, UserEditForm

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
    post_obj = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(post_id=post_id)
    if post_obj.author == request.user:
        return render(
            request,
            'blog/detail.html',
            {
                'post': post_obj,
                'form': CongratulationForm(),
                'comments': comments,
            },
        )
    post_obj = get_object_or_404(
        filter_published_posts(Post.objects), pk=post_id
    )
    return render(
        request,
        'blog/detail.html',
        {'post': post_obj, 'form': CongratulationForm(), 'comments': comments},
    )


class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        return filter_published_posts(Post.objects.all())


class CategoryListView(LoginRequiredMixin, ListView):
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


class UserProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'page_obj'
    paginate_by = 10

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


class CommentCreateView(CreateView):
    model = Comment
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

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentEditUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    fields = ('text',)
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        # Получаем комментарий до основной обработки
        self.comment = get_object_or_404(Comment, id=kwargs['comment_id'])

        # Проверяем авторство
        if not request.user == self.comment.author:
            raise PermissionDenied(
                "Вы не можете редактировать чужой комментарий"
            )

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentDeleteDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        self.comment = get_object_or_404(Comment, id=kwargs['comment_id'])
        if not request.user == self.comment.author:
            raise PermissionDenied("Вы не можете удалить чужой комментарий")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


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


class PostEditUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, id=kwargs['post_id'])
        print(self.post_obj)
        print(request.user.username)
        if request.user != self.post_obj.author:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostDeleteDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, id=kwargs['post_id'])
        print(self.post_obj)
        print(request.user.username)
        if request.user != self.post_obj.author:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:index')  # Изменено на редирект на главную страницу
