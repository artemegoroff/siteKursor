from django import forms
from .models import CommentEge


class CommentForm(forms.ModelForm):
    content = forms.CharField(label='',widget=forms.Textarea(attrs={'class':'form-control',
                                                                    'placeholder': 'Введите комментарий',
                                                                    'rows': '4', 'columns': '80'}))
    class Meta:
        model = CommentEge
        fields = ('content',)