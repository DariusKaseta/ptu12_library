from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from . import models


class BookInstanceInline(admin.TabularInline):
    model = models.BookInstance
    # readonly_fields = ('id', )
    can_delete = False
    extra = 0


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    list_filter = ('genre', )
    inlines = (BookInstanceInline, )


class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'due_back', 'reader', 'book')
    list_filter = ('status', 'due_back')
    list_editable = ('status', 'due_back', 'reader')
    readonly_fields = ('id', )
    search_fields = ('id', 'book__title')

    fieldsets = (
        (_('General'), {'fields': ('book', 'id')}),
        (_('Availability'), {'fields': ('status', ('due_back', 'reader'), )}),
    )


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'display_books')
    list_display_links = ('last_name', )


admin.site.register(models.Author, AuthorAdmin)
admin.site.register(models.Book, BookAdmin)
admin.site.register(models.Genre)
admin.site.register(models.BookInstance, BookInstanceAdmin)
