from django.shortcuts import render
import web.settings as sett
from .models import Slider_main,Slider_site,Banner
from django.utils import timezone
# Create your views here.




def media_admin(request):
    context = {
        'media_url':sett.MEDIA_URL
    }


    return context

def main(request):

    return render(request,'main_app/main.html')





def slider_list_view(request):
    # دریافت تمام اسلایدرها
    sliders = Slider_site.objects.all()

    # بررسی تاریخ انقضا و غیرفعال کردن اسلایدرهای منقضی‌شده
    for slider in sliders:
        slider.deactivate_if_expired()

    # فقط اسلایدرهای فعال را نمایش می‌دهیم
    active_sliders = Slider_site.objects.filter(is_active=True)

    return render(request, 'main_app/slider_file.html', {'sliders': active_sliders})

def slider_list_view2(request):
    # دریافت تمام اسلایدرها
    sliders = Slider_site.objects.all().order_by('register_data')[:2]

    # بررسی تاریخ انقضا و غیرفعال کردن اسلایدرهای منقضی‌شده
    for slider in sliders:
        slider.deactivate_if_expired()

    # فقط اسلایدرهای فعال را نمایش می‌دهیم
    active_sliders = Slider_site.objects.filter(is_active=True)

    return render(request, 'main_app/slider_file2.html', {'sliders': active_sliders})


def slider_main_view(request):
    sliders = Slider_main.objects.all().order_by('register_data')[:2]

    # بررسی تاریخ انقضا و غیرفعال کردن اسلایدرهای منقضی‌شده
    for slider in sliders:
        slider.deactivate_if_expired()

    # فقط اسلایدرهای فعال را نمایش می‌دهیم
    active_sliders = Slider_main.objects.filter(is_active=True)[:2]

    return render(request, 'main_app/slider_main.html', {'sliders': active_sliders})




def active_banners(request):
    banners = Banner.objects.filter(is_active=True, End_data__gt=timezone.now())
    return render(request, 'main_app/slider_banner.html', {'banners': banners})




def about(request):

    return render(request,'main_app/dsm/about.html')


def call(request):

    return render(request,'main_app/dsm/call.html')

def faq(request):

    return render(request,'main_app/dsm/faq.html')