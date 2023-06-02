from typing import Any
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.views import generic
from . models import Book, Author, BookInstance, Genre

def index(request):
    # Suskaičiuokime keletą pagrindinių objektų
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    
    # Laisvos knygos (tos, kurios turi statusą 'g')
    num_instances_available = BookInstance.objects.filter(status__exact=0).count()
    
    # Kiek yra autorių    
    num_authors = Author.objects.count()
    
    # perduodame informaciją į šabloną žodyno pavidale:
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
    }

    return render(request, 'library/index.html', context)

def author_list(request):
    qs = Author.objects
    query = request.GET.get('query')
    if query:
        qs = qs.filter(
            Q(last_name__istartswith=query) |
            Q(first_name__icontains=query)
        )
    else:
        qs = qs.all()
    paginator = Paginator(qs, 5)
    author_list = paginator.get_page(request.GET.get('page'))
    return render(request, 'library/authors.html', {
        'author_list': author_list,
    })

def author_detail(request, pk: int):
    return render(request, 'library/author_detail.html', {
        'author': get_object_or_404(Author, pk=pk)
    })


class BookListView(generic.ListView):
    model = Book
    paginate_by = 6
    template_name = 'library/book_list.html'

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        query = self.request.GET.get('query')
        if query:
            qs = qs.filter(
                Q(title__icontains=query) |
                Q(summary__icontains=query) |
                Q(author__last_name__istartswith=query)
            )
        return qs


class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'library/book_detail.html'
