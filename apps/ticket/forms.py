# forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Ticket, TicketMessage, TicketDepartment, TicketPriority

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['department', 'priority', 'subject']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'موضوع تیکت را وارد کنید...'
            }),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'subject': 'موضوع تیکت',
            'department': 'دپارتمان مربوطه',
            'priority': 'اولویت',
        }

class TicketMessageForm(forms.ModelForm):
    class Meta:
        model = TicketMessage
        fields = ['message', 'file']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'پیام خود را وارد کنید...'
            }),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'message': 'پیام',
            'file': 'فایل پیوست (اختیاری)',
        }

class TicketFilterForm(forms.Form):
    STATUS_CHOICES = [
        ('', 'همه وضعیت‌ها'),
        ('open', 'تیکت‌های باز'),
        ('closed', 'تیکت‌های بسته'),
        ('unread', 'تیکت‌های خوانده نشده'),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    department = forms.ModelChoiceField(
        queryset=TicketDepartment.objects.filter(is_active=True),
        required=False,
        empty_label="همه دپارتمان‌ها",
        widget=forms.Select(attrs={'class': 'form-select'})
    )