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
    list_display = ('id', 'status', 'due_back', 'book')
    list_filter = ('status', 'due_back')
    readonly_fields = ('id', )

    fieldsets = (
        (_('General'), {'fields': ('book', 'id')}),
        (_('Availability'), {'fields': (('status', 'due_back'), )}),
    )


admin.site.register(models.Author)
admin.site.register(models.Book, BookAdmin)
admin.site.register(models.Genre)
admin.site.register(models.BookInstance, BookInstanceAdmin)
