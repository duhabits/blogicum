from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django.utils import timezone

from .const import PAGINATE_BY
from .forms import CommentForm, PostForm, UserEditForm
from .models import Category, Post
from core.mixins import AuthorCheckMixin, CommentMixin, PostMixin
from core.utils import filter_published_posts, annotate_with_comment_count

User = get_user_model()


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"
    pk_url_kwarg = "post_id"

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs["post_id"])
        if self.request.user == post.author:
            return post

        now = timezone.now()
        category_ok = post.category is None or (
            post.category.is_published and bool(post.category.slug)
        )

        post_is_visible = (
            post.is_published and post.pub_date <= now and category_ok
        )

        if not post_is_visible:
            raise Http404("Пост не доступен")

        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = self.object.comments.select_related("author")
        return context


class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        return annotate_with_comment_count(
            filter_published_posts(Post.objects.all())
        )


class CategoryListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = PAGINATE_BY

    def get_category(self):
        return get_object_or_404(
            Category, is_published=True, slug=self.kwargs['category_slug']
        )

    def get_queryset(self) -> QuerySet[Any]:
        return filter_published_posts(self.get_category().posts)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class UserProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'page_obj'
    paginate_by = PAGINATE_BY

    def get_author(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self) -> QuerySet[Any]:
        queryset = annotate_with_comment_count(self.get_author().posts)

        if self.request.user != self.get_author():
            queryset = filter_published_posts(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_author()
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


class CommentCreateView(CommentMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentEditUpdateView(CommentMixin, AuthorCheckMixin, UpdateView):
    pass


class CommentDeleteDeleteView(CommentMixin, AuthorCheckMixin, DeleteView):
    pass


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


class PostEditUpdateView(PostMixin, UpdateView):
    form_class = PostForm


class PostDeleteDeleteView(PostMixin, DeleteView):
    pass


class AuthCreateView(CreateView):
    template_name = ('registration/registration_form.html',)
    form_class = (UserCreationForm,)
    success_url = reverse_lazy('blog:index')
