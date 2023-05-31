from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
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
    return render(request, 'library/authors.html', {
        'author_list': Author.objects.all()
    })

def author_detail(request, pk: int):
    return render(request, 'library/author_detail.html', {
        'author': get_object_or_404(Author, pk=pk)
    })
