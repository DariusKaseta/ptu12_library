from django import forms
from . import models


class DateInput(forms.DateInput):
    input_type = 'date'


class BookReviewForm(forms.ModelForm):
    class Meta:
        model = models.BookReview
        fields = ('content', 'book', 'reviewer')
        widgets = {
            'book': forms.HiddenInput(),
            'reviewer': forms.HiddenInput(),
        }


class BookInstanceForm(forms.ModelForm):
    class Meta:
        model = models.BookInstance
        fields = ('book', 'due_back', 'reader', 'status')
        widgets = {
            'book': forms.HiddenInput(),
            'reader': forms.HiddenInput(),
            'due_back': DateInput(),
            'status': forms.HiddenInput(),
        }
