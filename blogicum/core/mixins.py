from blog.models import Comment, Post
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView
from django.http import HttpResponseForbidden


class CommentMixinView:
    model = Comment

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentAccessMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        self.comment = get_object_or_404(Comment, id=kwargs['comment_id'])
        if request.user != self.comment.author:
            return HttpResponseForbidden(
                "Вы не можете изменять чужой комментарий"
            )
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.comment

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = self.comment
        return context


class PostMixinView(LoginRequiredMixin):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, id=kwargs['post_id'])
        if request.user != self.post_obj.author:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:index')
