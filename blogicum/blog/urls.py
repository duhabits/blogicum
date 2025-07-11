from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path(
        'posts/<int:post_id>/',
        views.post_detail,
        name='post_detail',
    ),
    path(
        'category/<slug:category_slug>/',
        views.СategoryListView.as_view(),
        name='category_posts',
    ),
    path(
        'profile/<str:username>/',
        views.UserProfileView.as_view(),
        name='profile',
    ),
    path(
        'posts/<int:post_id>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment',
    ),
]