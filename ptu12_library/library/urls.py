from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('authors/', views.author_list, name='author_list'),
    path('author/<int:pk>/', views.author_detail, name='author_detail'),
    path('books/', views.BookListView.as_view(), name='book_list'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('books/my/', views.UserBookInstanceListView.as_view(), name='user_book_instances'),
    path('book/reserve/', views.BookInstanceCreateView.as_view(), name='bookinstance_create'),

]
