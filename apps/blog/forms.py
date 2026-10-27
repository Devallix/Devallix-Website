from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Name or Nickname',
            'autocomplete': 'name',
            'id': 'comment_name_input'
        })
    )
    body = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Share your thoughts, questions, or feedback...',
            'rows': 4,
            'id': 'comment_body_input'
        })
    )

    class Meta:
        model = Comment
        fields = ['name', 'body']

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError('Please enter a name with at least 2 characters.')
        return name

    def clean_body(self):
        body = self.cleaned_data.get('body', '').strip()
        if len(body) < 3:
            raise forms.ValidationError('Comment content must be at least 3 characters long.')
        return body
