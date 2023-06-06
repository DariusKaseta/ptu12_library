from django.contrib.auth import get_user_model
from datetime import date
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from tinymce.models import HTMLField
import uuid

User = get_user_model()


class Genre(models.Model):
    name = models.CharField(_("name"), max_length=100)

    class Meta:
        verbose_name = _("genre")
        verbose_name_plural = _("genres")

    def __str__(self):
        return self.name


class Author(models.Model):
    first_name = models.CharField(_("first name"), max_length=50, db_index=True)
    last_name = models.CharField(_("last name"), max_length=50, db_index=True)
    biography = HTMLField(_("biography"), max_length=8000, blank=True, null=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = _("author")
        verbose_name_plural = _("authors")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse("author_detail", kwargs={"pk": self.pk})

    def display_books(self):
        return ', '.join(book.title for book in self.books.all()[:3])
    display_books.short_description = _('books')


class Book(models.Model):
    title = models.CharField(_("title"), max_length=250, db_index=True)
    summary = HTMLField(_("summary"), max_length=4000)
    author = models.ForeignKey(
        Author, 
        verbose_name=_("author"), 
        on_delete=models.CASCADE,
        related_name='books',
    )
    genre = models.ManyToManyField(
        Genre, 
        verbose_name=_("genre(s)"), 
        help_text=_("choose genre(s) for this book")
    )
    cover = models.ImageField(
        _("cover"), 
        upload_to='library/book_covers', 
        null=True, 
        blank=True,
    )

    class Meta:
        ordering = ['title']
        verbose_name = _("book")
        verbose_name_plural = _("books")

    def __str__(self):
        return f"{self.author} - {self.title}"

    def get_absolute_url(self):
        return reverse("book_detail", kwargs={"pk": self.pk})

    def display_genre(self):
        return ', '.join(genre.name for genre in self.genre.all()[:3])
    display_genre.short_description = _('genre')


class BookInstance(models.Model):
    id = models.UUIDField(_("ID"), primary_key=True, default=uuid.uuid4)
    book = models.ForeignKey(
        Book, 
        verbose_name=_("book"), 
        on_delete=models.CASCADE,
        related_name='instances',
    )
    due_back = models.DateField(_("due back"), null=True, blank=True, db_index=True)
    reader = models.ForeignKey(
        User, 
        verbose_name=_("reader"), 
        on_delete=models.CASCADE,
        related_name='book_instances',
        null=True, blank=True,
    )

    STATUS_CHOICES = (
        (0, _('Available')),
        (1, _('Reserved')),
        (2, _('Taken')),
        (3, _('Unavailable')),
        (7, _('Broken')),
    )
    
    status = models.PositiveSmallIntegerField(
        _("status"), 
        choices=STATUS_CHOICES, 
        default=0,
        db_index=True
    )

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    class Meta:
        ordering = ['due_back']
        verbose_name = _("book instance")
        verbose_name_plural = _("book instances")

    def __str__(self):
        return f"{self.book.title} - {self.get_status_display()}"

    def get_absolute_url(self):
        return reverse("bookinstance_detail", kwargs={"pk": self.pk})
