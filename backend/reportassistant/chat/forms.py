from typing import Optional


from django import forms
from django.contrib.auth.models import User

from db_configurator.models import Status, DatabaseSource


class MessageForm(forms.Form):
    user_message = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Type your message...',
            'rows': 2,
            'class': 'form-control'
        }),
        label='',
        max_length=1000
    )

    database_source = forms.ModelChoiceField(
        queryset=DatabaseSource.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Select Data Source',
        empty_label="Choose a source"
    )

    def __init__(self, *args, **kwargs):
        user: Optional[User] = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            if not user.is_superuser:
                user_groups = user.groups.all()
                self.fields['database_source'].queryset = DatabaseSource.objects.filter(
                    group__in=user_groups,
                    status=Status.READY.value
                )
            else:
                self.fields['database_source'].queryset = DatabaseSource.objects.filter(
                    status=Status.READY.value
                )
        self.fields['database_source'].label_from_instance = lambda obj: obj.display_name
