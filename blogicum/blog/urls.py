from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path(
        'posts/<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail',
    ),
    path(
        'category/<slug:category_slug>/',
        views.CategoryListView.as_view(),
        name='category_posts',
    ),
    path(
        'profile/edit/',
        views.UserProfileUpdateView.as_view(),
        name='edit_profile',
    ),
    path(
        'profile/<str:username>/',
        views.UserProfileListView.as_view(),
        name='profile',
    ),
    path(
        'posts/<int:post_id>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment',
    ),
    path(
        'posts/<int:post_id>/comment/edit_comment/<int:comment_id>/',
        views.CommentEditUpdateView.as_view(),
        name='edit_comment',
    ),
    path(
        'posts/<int:post_id>/comment/delete_comment/<int:comment_id>/',
        views.CommentDeleteDeleteView.as_view(),
        name='delete_comment',
    ),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path(
        'posts/<int:post_id>/edit/',
        views.PostEditUpdateView.as_view(),
        name='edit_post',
    ),
    path(
        'posts/<int:post_id>/delete/',
        views.PostDeleteDeleteView.as_view(),
        name='delete_post',
    ),
]
