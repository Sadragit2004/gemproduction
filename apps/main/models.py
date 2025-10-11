from django.db import models
import utils
from django.utils import timezone
import os  # Standard library imports
from PIL import Image

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _



# Create your models here.
class Slider_site(models.Model):
    text_slider = models.CharField(max_length=100,verbose_name='متن اسلایدر')
    image_file = utils.FileUpload('images','slider')
    image_name = models.ImageField(upload_to=image_file.upload_to,verbose_name='عکس اسلایدر')
    alt_slide = models.CharField(verbose_name='نوشتار عکس',max_length=100)
    is_active = models.BooleanField(verbose_name='فعال',default=True)
    register_data = models.DateTimeField(verbose_name='تاریخ شروع',default=timezone.now)
    End_data = models.DateTimeField(verbose_name='تاریخ پایان',default=timezone.now)
    link = models.CharField(max_length=300,verbose_name='لینک',null=True,blank=True)

    def __str__(self) -> str:
        return self.text_slider


    def deactivate_if_expired(self):
        if self.End_data and self.End_data < timezone.now():
            self.is_active = False
            self.save()

    class Meta:
        verbose_name = 'اسلایدر'
        verbose_name_plural = 'اسلایدرها'



class Slider_main(models.Model):
    text_slider = models.CharField(max_length=100,verbose_name='متن اسلایدر')
    image_file = utils.FileUpload('images','slider')
    image_name = models.ImageField(upload_to=image_file.upload_to,verbose_name='عکس اسلایدر')
    alt_slide = models.CharField(verbose_name='نوشتار عکس',max_length=100,blank=True,null=True)
    is_active = models.BooleanField(verbose_name='فعال',default=True)
    register_data = models.DateTimeField(verbose_name='تاریخ شروع',default=timezone.now)
    End_data = models.DateTimeField(verbose_name='تاریخ پایان',default=timezone.now)
    link = models.CharField(max_length=300,verbose_name='لینک',null=True,blank=True)

    def __str__(self) -> str:
        return self.text_slider


    def deactivate_if_expired(self):
        if self.End_data and self.End_data < timezone.now():
            self.is_active = False
            self.save()

    class Meta:
        verbose_name = 'اسلایدر مرکز'
        verbose_name_plural = 'اسلایدرها مرکز ها'




class Banner(models.Model):

    name_banner = models.CharField(max_length=100,verbose_name='نام بنر')
    text_banner = models.CharField(max_length=300,verbose_name='متن بنر')
    alt_slide = models.CharField(verbose_name='نوشتار عکس',max_length=100,blank=True,null=True)
    image_file = utils.FileUpload('images','banners')
    image_name = models.ImageField(upload_to=image_file.upload_to)
    is_active = models.BooleanField(default=False,)
    register_data = models.DateTimeField(verbose_name='تاریخ شروع',default=timezone.now)
    End_data = models.DateTimeField(verbose_name='تاریخ پایان',default=timezone.now)




    def deactivate_if_expired(self):
        if self.End_data and self.End_data < timezone.now():
            self.is_active = False
            self.save()




def validate_image_or_svg(file):
    """
    Validator to check if the uploaded file is an image or an SVG.
    """
    ext = os.path.splitext(file.name)[1].lower()
    if ext == '.svg':
        return  # Valid SVG file
    try:
        img = Image.open(file)
        img.verify()
    except Exception as exc:
        raise ValidationError(
            _('Invalid file. Only images or SVGs are allowed.')
        ) from exc



class InfoCompany(models.Model):

    name_company = models.CharField(max_length=100,verbose_name='نام شرکت')
    phone_number = models.CharField(max_length=11,verbose_name='نام شماره',blank=True,null=True)
    mobile_number = models.CharField(max_length=11,verbose_name='تلفن همراه',blank=True,null=True)
    image_file = utils.FileUpload('images','logo')
    logo_name = models.FileField(upload_to=image_file.upload_to,validators=[validate_image_or_svg])
    register_data = models.DateTimeField(verbose_name='تاریخ شروع',default=timezone.now)


    def __str__(self):
        return f'{self.name_company}'


    class Meta:
        verbose_name = 'اطلاعات شرکت'
        verbose_name_plural = 'اطلاعات های شرکت'


class MetaTagMainPage(models.Model):

    title_header = models.CharField(max_length=100,verbose_name='عنوان صفحه')
    title_og = models.CharField(max_length=100,verbose_name='عنوان صفحه og')
    description = models.TextField(verbose_name='توضیحات صفحه')
    keywordf = models.CharField(max_length=100,verbose_name='لیست کلمات کلیدی')
    created_at = models.DateTimeField(verbose_name='ساخته شده در تاریخ',default=timezone.now)
    updated_at = models.DateTimeField(auto_now_add=True,verbose_name='تاریخ اپدیت')

    class Meta:

        verbose_name = 'متا تگ'
        verbose_name_plural = 'متا تگ ها'

    def __str__(self):
        return f'{self.title_header}'

