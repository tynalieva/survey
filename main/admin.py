from django.contrib import admin
from .models import *


class ImageInline(admin.TabularInline):
    model = Image
    fields = ('image', )
    max_num = 3


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [ImageInline, ]


# admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Favorites)
admin.site.register(Rating)
