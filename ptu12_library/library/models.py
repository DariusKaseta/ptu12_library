from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


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

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = _("author")
        verbose_name_plural = _("authors")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse("author_detail", kwargs={"pk": self.pk})


class Book(models.Model):
    title = models.CharField(_("title"), max_length=250, db_index=True)
    summary = models.TextField(_("summary"), max_length=4000)
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

    class Meta:
        ordering = ['title']
        verbose_name = _("book")
        verbose_name_plural = _("books")

    def __str__(self):
        return f"{self.author} - {self.title}"

    def get_absolute_url(self):
        return reverse("book_detail", kwargs={"pk": self.pk})
