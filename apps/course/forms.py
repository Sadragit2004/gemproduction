# your_app/forms.py

from django import forms
from .models import CourseRating, CourseComment

class CourseRatingForm(forms.ModelForm):
    """
    فرم برای ثبت یا به‌روزرسانی امتیاز کاربر به یک دوره.
    """
    class Meta:
        model = CourseRating
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, str(i)) for i in range(1, 6)], attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'نظر خود را بنویسید (اختیاری)'}),
        }
        labels = {
            'rating': 'امتیاز شما',
            'comment': 'نظر شما',
        }

class CourseCommentForm(forms.ModelForm):
    """
    فرم برای ثبت کامنت جدید برای یک دوره.
    """
    class Meta:
        model = CourseComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'کامنت خود را اینجا بنویسید...'}),
        }
        labels = {
            'comment': 'متن کامنت',
        }