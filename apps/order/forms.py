from django import forms

class CustomerForm(forms.Form):
    name = forms.CharField(label='',error_messages={'required':'این فیلد نمیتواند خالی باشد'},
                           widget=forms.TextInput(attrs={'class':'peer w-full rounded-lg border-none bg-transparent px-4 py-3 placeholder-transparent focus:outline-none focus:ring-0','placeholder':'نام'}))

    family = forms.CharField(label='',
                             error_messages={'required':'این فیلد نمیتواند خالی باشد'},
                             widget=forms.TextInput(attrs={'class':'peer w-full rounded-lg border-none bg-transparent px-4 py-3 placeholder-transparent focus:outline-none focus:ring-0','placeholder':'نام خانوادگی'}))


    descript = forms.CharField(label='',
                             required=False,
                             widget=forms.Textarea(attrs={'class':'peer w-full rounded-lg border-none bg-transparent px-4 py-3 placeholder-transparent focus:outline-none focus:ring-0','placeholder':'توضیحات'}))


    # peyment_type = forms.ChoiceField(label='',choices=[(pay.pk,pay) for pay in PeymentType.objects.all()],widget=forms.RadioSelect(attrs={'class':''}))





