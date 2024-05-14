from django.contrib import admin

from .models import Post, Category, Location


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    search_fields = ('text',)
    list_display = (
        'id',
        'title',
        'author',
        'text',
        'category',
        'pub_date',
        'location',
        'is_published',
        'created_at',
    )
    list_display_links = ('title',)
    list_editable = (
        'category',
        'location',
        'is_published',
    )
    list_filer = ('created_at', )
    empty_value_display = '-пусто-'

    @admin.register(Category)
    class CategoryAdmin(admin.ModelAdmin):
        ...

    @admin.register(Location)
    class LocationAdmin(admin.ModelAdmin):
        ...
