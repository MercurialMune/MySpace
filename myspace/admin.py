from django.contrib import admin
from .models import Post, Category, tags


# Post registration

class PostAdmin( admin.ModelAdmin ):
    list_display = ('title', 'slug', 'author', 'status', 'created')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'author')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']


admin.site.register( Post, PostAdmin )
admin.site.register( tags )


class CategoryAdmin( admin.ModelAdmin ):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    exclude = ('post_ids',)  # exclude post ids filed coz we handled it with a receiver


admin.site.register( Category, CategoryAdmin )
