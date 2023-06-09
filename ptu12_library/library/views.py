from typing import Any, Dict, Optional
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.core.paginator import Paginator
from datetime import date, timedelta
from django.db.models.query import QuerySet
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import generic
from . forms import BookReviewForm, BookInstanceForm
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


class BookInstanceCreateView(LoginRequiredMixin, generic.CreateView):
    model = BookInstance
    form_class = BookInstanceForm
    template_name = 'library/bookinstance_form.html'
    success_url = reverse_lazy('user_book_instances')

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['book'] = self.book
        return context

    def get_initial(self) -> Dict[str, Any]:
        self.book = get_object_or_404(Book, id=self.request.GET.get('book_id'))
        initial = super().get_initial()
        initial['book'] = self.book
        initial['reader'] = self.request.user
        initial['due_back'] = date.today() + timedelta(days=14)
        initial['status'] = 1
        return initial

    def form_valid(self, form):
        form.instance.book = self.book
        form.instance.reader = self.request.user
        form.instance.status = 1
        return super().form_valid(form)


class BookInstanceUpdateView(
    LoginRequiredMixin, 
    UserPassesTestMixin, 
    generic.UpdateView
):
    model = BookInstance
    form_class = BookInstanceForm
    template_name = 'library/bookinstance_form.html'
    success_url = reverse_lazy('user_book_instances')

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context['book'] = obj.book
        if obj.status == 1:
            context['taking'] = True
        else:
            context['extending'] = True
        return context

    def get_initial(self) -> Dict[str, Any]:
        initial = super().get_initial()
        initial['due_back'] = date.today() + timedelta(days=14)
        initial['status'] = 2
        return initial

    def form_valid(self, form):
        form.instance.reader = self.request.user
        form.instance.status = 2
        return super().form_valid(form)

    def test_func(self) -> bool | None:
        obj = self.get_object()
        return obj.reader == self.request.user


class BookInstanceDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.DeleteView
):
    model = BookInstance
    template_name = 'library/user_bookinstance_delete.html'
    success_url = reverse_lazy('user_book_instances')

    def test_func(self) -> bool | None:
        obj = self.get_object()
        return obj.reader == self.request.user
