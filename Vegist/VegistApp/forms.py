from django import forms

from .models import Review

class ReviewForm(forms.ModelForm):
    review = forms.CharField(widget=forms.Textarea(attrs={'placeholder':'Write Review'}))

    class Meta:
        model = Review
        fields = ['review','rating']