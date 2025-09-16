from blog.models import Comment, Post
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponseForbidden


class AuthorCheckMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user == self.get_object().author


class PostMixin(AuthorCheckMixin, LoginRequiredMixin):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse('blog:index')

    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            return HttpResponseForbidden(
                "У вас нет прав для выполнения этого действия"
            )
        return reverse(
            'blog:post',
            kwargs={
                'username': get_object_or_404(Post, pk=self.kwargs['post_id'])
            },
        )


class CommentMixin(LoginRequiredMixin):
    model = Comment
    fields = ('text',)
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )
