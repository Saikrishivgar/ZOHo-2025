from django import forms
from .models import ClientEntry

class ClientEntryForm(forms.ModelForm):
    class Meta:
        model = ClientEntry
        fields = ['location', 'department', 'name', 'email', 'notes']
        
