from django import forms

class MessageForm(forms.Form):
    user_message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Type your message...', 'rows': 2, 'class': 'form-control'}), label='', max_length=1000)
