from typing import Any, Dict
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic
from . forms import BookReviewForm
from . models import Book, Author, BookInstance, Genre

def index(request):
    # Suskaičiuokime keletą pagrindinių objektų
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    
    # Laisvos knygos (tos, kurios turi statusą 'g')
    num_instances_available = BookInstance.objects.filter(status__exact=0).count()
    
    # Kiek yra autorių    
    num_authors = Author.objects.count()

    # Apsilankymų skaitliukas
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1
    
    # perduodame informaciją į šabloną žodyno pavidale:
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
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


class BookDetailView(generic.edit.FormMixin, generic.DetailView):
    model = Book
    template_name = 'library/book_detail.html'
    form_class = BookReviewForm

    def get_initial(self) -> Dict[str, Any]:
        initial = super().get_initial()
        initial['book'] = self.get_object()
        initial['reviewer'] = self.request.user
        return initial

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
        
    def form_valid(self, form: Any) -> HttpResponse:
        form.instance.book = self.get_object()
        form.instance.reviewer = self.request.user
        form.save()
        messages.success(self.request, _('Review posted!'))
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('book_detail', kwargs={'pk':self.get_object().pk})


class UserBookInstanceListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'library/user_bookinstance_list.html'
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        qs = qs.filter(reader=self.request.user)
        return qs
