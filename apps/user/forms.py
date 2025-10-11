from django import forms
import re


class MobileForm(forms.Form):
    mobileNumber = forms.CharField(
        max_length=11,
        min_length=11,
        label="شماره موبایل",
        widget=forms.TextInput(attrs={
            "placeholder": "شماره موبایل خود را وارد کنید",
            "class": "peer w-full rounded-lg border-none bg-transparent p-4 text-left placeholder-transparent focus:outline-none focus:ring-0"
        })
    )

    def clean_mobileNumber(self):
        mobile = self.cleaned_data.get("mobileNumber")

        # فقط اعداد باشه
        if not mobile.isdigit():
            raise forms.ValidationError("شماره موبایل فقط باید شامل اعداد باشد.")

        # دقیقا 11 رقم باشه
        if len(mobile) != 11:
            raise forms.ValidationError("شماره موبایل باید 11 رقم باشد.")

        # شماره ایرانی باشه (با 09 شروع بشه)
        if not re.match(r"^09\d{9}$", mobile):
            raise forms.ValidationError("شماره موبایل معتبر ایرانی نیست.")

        return mobile


class VerificationCodeForm(forms.Form):
    code1 = forms.CharField(
        max_length=1,
        min_length=1,
        label='',
        widget=forms.TextInput(attrs={
            'inputmode': 'numeric',
            'class': 'otp-input h-14 w-14 rounded-lg border bg-muted text-center text-lg outline-none xs:h-16 xs:w-16 md:text-xl',
            'placeholder': ''
        })
    )
    
    code2 = forms.CharField(max_length=1, min_length=1, label='', widget=forms.TextInput(attrs={'inputmode':'numeric','class':'otp-input h-14 w-14 rounded-lg border bg-muted text-center text-lg outline-none xs:h-16 xs:w-16 md:text-xl'}))
    code3 = forms.CharField(max_length=1, min_length=1, label='', widget=forms.TextInput(attrs={'inputmode':'numeric','class':'otp-input h-14 w-14 rounded-lg border bg-muted text-center text-lg outline-none xs:h-16 xs:w-16 md:text-xl'}))
    code4 = forms.CharField(max_length=1, min_length=1, label='', widget=forms.TextInput(attrs={'inputmode':'numeric','class':'otp-input h-14 w-14 rounded-lg border bg-muted text-center text-lg outline-none xs:h-16 xs:w-16 md:text-xl'}))
    code5 = forms.CharField(max_length=1, min_length=1, label='', widget=forms.TextInput(attrs={'inputmode':'numeric','class':'otp-input h-14 w-14 rounded-lg border bg-muted text-center text-lg outline-none xs:h-16 xs:w-16 md:text-xl'}))

    def clean(self):
        cleaned_data = super().clean()
        code = ''.join([
            cleaned_data.get('code1', ''),
            cleaned_data.get('code2', ''),
            cleaned_data.get('code3', ''),
            cleaned_data.get('code4', ''),
            cleaned_data.get('code5', ''),
        ])

        if not code.isdigit():
            raise forms.ValidationError("کد تأیید فقط باید شامل اعداد باشد.")

        if len(code) != 5:
            raise forms.ValidationError("کد تأیید باید دقیقا ۵ رقم باشد.")

        # کد نهایی رو توی cleaned_data ذخیره می‌کنیم
        cleaned_data['activeCode'] = code
        return cleaned_data