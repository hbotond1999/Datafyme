from django import forms
from .models import DatabaseSource, DBType


def get_db_types():
    db_choices = []
    for db_type in DBType:
        db_choices.append((db_type.value, db_type.value))
    return db_choices

class DatabaseSourceForm(forms.ModelForm):
    class Meta:
        model = DatabaseSource
        fields = ['type', 'name', 'username', 'password', 'host', 'port', 'display_name']
        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }

    type = forms.ChoiceField(
        choices=get_db_types(),
        widget=forms.Select
    )
