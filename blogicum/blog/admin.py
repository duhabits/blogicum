from django.contrib import admin

from .models import Post, Category, Location, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at',
    )
    list_display_links = ('title',)
    list_filter = ('is_published',)
    search_fields = ('title',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
        'created_at',
    )
    list_filter = ('created_at',)
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'description',
        'is_published',
        'created_at',
    )
    list_filter = ('created_at',)
    search_fields = ('title',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'post',
        'author',
    )
    list_filter = ('created_at',)
    search_fields = ('author',)
