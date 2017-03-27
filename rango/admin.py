from django.contrib import admin
from rango.models import Category, Page

# admin.site.register(Category)
# admin.site.register(Page)


class PageAdmin(admin.ModelAdmin):
    list_display = ('category', 'title', 'url')

admin.site.register(Page, PageAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'views', 'likes')
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Category, CategoryAdmin)


from rango.models import UserProfile

admin.site.register(UserProfile)
