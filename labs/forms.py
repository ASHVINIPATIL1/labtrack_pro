from django import forms
from .models import Department, Lab, Device, DeviceCategory


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Computer Science'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. C Building, 4th Floor'}),
        }


class LabForm(forms.ModelForm):
    class Meta:
        model = Lab
        fields = ['department', 'name', 'location', 'description']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Computer Lab A'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Room 101, Block B'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = [
            'serial_id', 'name', 'category', 'os_name', 'software_details', 'quantity',
            'purchase_cost', 'purchase_date', 'useful_life_years', 'salvage_value',
            'min_threshold', 'notes'
        ]
        widgets = {
            'serial_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Device ID'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Dell OptiPlex 7090'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'os_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Windows 11 or None'}),
            'software_details': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MS Office, AutoCAD or None'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'purchase_cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'useful_life_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'salvage_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'min_threshold': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class DeviceCategoryForm(forms.ModelForm):
    class Meta:
        model = DeviceCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class DeviceStatusForm(forms.Form):
    STATUS_CHOICES = [
        ('working', 'Working'),
        ('maintenance', 'Maintenance'),
        ('trash', 'Trash'),
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Reason for status change...'})
    )