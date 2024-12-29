from typing import Optional

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from db_configurator.models import Status, DatabaseSource


class MessageForm(forms.Form):
    user_message = forms.CharField(

        widget=forms.Textarea(attrs={
            'id': "chatUserMessage",
            'placeholder': _('Type your message...'),
            'rows': 2,
            'class': 'form-control'
        }),
        label='',
        max_length=1000
    )

    database_source = forms.ModelChoiceField(
        queryset=DatabaseSource.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label=_("Choose a source")
    )

    def __init__(self, *args, **kwargs):
        user: Optional[User] = kwargs.pop('user', None)
        database_source_id: Optional[int] = kwargs.pop('database_source_id', None)
        super().__init__(*args, **kwargs)

        # Set queryset for database_source field based on user permissions
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

        if database_source_id is not None:
            try:
                default_source = DatabaseSource.objects.get(id=database_source_id)
                if default_source in self.fields['database_source'].queryset:
                    self.fields['database_source'].initial = default_source
            except DatabaseSource.DoesNotExist:
                pass  # Handle the case where the ID is invalid

        # Customize label representation
        self.fields['database_source'].label_from_instance = lambda obj: obj.display_name
