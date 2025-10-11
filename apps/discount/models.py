from django.db import models
from apps.file.models import *
from django.core.validators import MaxValueValidator,MinValueValidator
from datetime import datetime

# Create your models here.
class Copon(models.Model):
    Copon = models.CharField(max_length=10,verbose_name='کد تخفیف',unique=True)
    start_date = models.DateTimeField(verbose_name='تاریخ شروع',default=timezone.now())
    end_date = models.DateTimeField(verbose_name='تاریخ پایان',default=timezone.now())
    discount = models.IntegerField(verbose_name='درصد تخفیف')
    isActive = models.BooleanField(verbose_name='فعال',default=False,)

    def __str__(self) -> str:
        return f'{self.Copon}'


    class Meta:
        verbose_name = 'کوپن تخفیف'
        verbose_name_plural = 'کوپن تخفیفات'




class Discount_basket(models.Model):
    discount_title = models.CharField(max_length=100,verbose_name='وضوع تخفیف')
    start_date = models.DateTimeField(verbose_name='تاریخ شروع',default=timezone.now())
    end_date = models.DateTimeField(verbose_name='تاریخ پایان',default=timezone.now())
    discount = models.IntegerField(verbose_name='درصد تخفیف', validators=[MinValueValidator(0), MaxValueValidator(100)])
    isActive = models.BooleanField(verbose_name='وضعیت',default=False)


    class Meta:
        verbose_name = ' سبد تخفیف '
        verbose_name_plural =  'سبد تخفیف ها '



class Discount_detail(models.Model):
    discountBasket = models.ForeignKey(Discount_basket,on_delete=models.CASCADE,verbose_name='سبد تخفیف',related_name='discount_of_basket')
    files = models.ForeignKey(File,on_delete=models.CASCADE,verbose_name='سایت',related_name='site_of_discount')



    class Meta:
        verbose_name = 'جزییات سبد خرید'
        verbose_name_plural = 'جزییات سبد تخفیف ها'

