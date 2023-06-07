from django import forms
from . import models


class BookReviewForm(forms.ModelForm):
    class Meta:
        model = models.BookReview
        fields = ('content', 'book', 'reviewer')
        widgets = {
            'book': forms.HiddenInput(),
            'reviewer': forms.HiddenInput(),
        }
