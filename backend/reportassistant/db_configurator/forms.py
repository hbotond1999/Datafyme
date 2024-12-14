from django import forms
from .models import DatabaseSource, DBType

class DatabaseSourceForm(forms.ModelForm):
    class Meta:
        model = DatabaseSource
        fields = ['type', 'name', 'username', 'password', 'host', 'port', 'display_name']
        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }

    type = forms.ChoiceField(
        choices=[(db_type.value, db_type.value) for db_type in DBType],
        widget=forms.Select
    )
