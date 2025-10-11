from django import forms
from apps.user.models import CustomUser

class EditProfileForm(forms.Form):
    name = forms.CharField(
        max_length=60,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'peer w-full rounded-lg border-none bg-transparent px-4 py-3 text-left placeholder-transparent focus:outline-none focus:ring-0',
            'id': 'name',
            'dir': 'auto'
        })
    )

    family = forms.CharField(
        max_length=60,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'peer w-full rounded-lg border-none bg-transparent px-4 py-3 text-left placeholder-transparent focus:outline-none focus:ring-0',
            'id': 'family',
            'dir': 'auto'
        })
    )

    GENDER_CHOICES = [
        ('male', 'مرد'),
        ('female', 'زن'),
    ]

    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-lg border bg-muted p-2 text-text/90 outline-none focus:ring-0 dark:placeholder-zinc-400',
            'id': 'gender'
        })
    )

    # فیلد تاریخ تولد
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'peer w-full rounded-lg border-none bg-transparent px-4 py-3 text-left placeholder-transparent focus:outline-none focus:ring-0',
            'id': 'birth_date'
        })
    )


