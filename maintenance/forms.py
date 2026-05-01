from django import forms
from .models import MaintenanceRequest


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['issue_description', 'priority']
        widgets = {
            'issue_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }


class PublicIssueForm(forms.Form):
    device_id = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Device ID (e.g. LAB1-0001)'
    }))
    issue_description = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 4,
        'placeholder': 'Describe the issue'
    }))


class ResolveForm(forms.Form):
    status = forms.ChoiceField(
        choices=MaintenanceRequest.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    resolution_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes or action taken'})
    )