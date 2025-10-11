from django.shortcuts import render,get_object_or_404,redirect

from django.contrib.auth.decorators import login_required
from apps.order.models import Order, OrderStatus
from django.conf import settings
from django.http import FileResponse, Http404,HttpResponse, HttpResponseServerError
import os
import requests

# Create your views here.


@login_required
def dashboard_view(request):

    current_user = request.user

    user_orders = Order.objects.filter(user=current_user).order_by('-createAt')

    current_orders = user_orders.filter(
        status__in=[
            OrderStatus.PENDING,
            OrderStatus.CONFIRMED,
            OrderStatus.ON_HOLD
        ]
    )

    delivered_orders = user_orders.filter(status=OrderStatus.DELIVERED)
    cancelled_orders = user_orders.filter(status=OrderStatus.CANCELLED)
    refunded_orders = user_orders.filter(status=OrderStatus.REFUNDED)

    # آماده‌سازی context برای ارسال به تمپلیت
    context = {
        # لیست‌ها برای نمایش آمار در بالای صفحه
        'success': current_orders,
        'arrived': delivered_orders,
        'failed': cancelled_orders,  # کلمه faield در تمپلیت به failed اصلاح شد
        'returned_orders': refunded_orders, # کلمه return در پایتون رزرو شده است

        # لیست سفارش‌های فعلی برای نمایش جزئیات
        'order_list': current_orders[:8],

        # داده‌های موقت چون مدل مربوطه ارائه نشده است
        'len_favorit': 0,
        'len_not_seen': 0,
    }

    # نام فایل تمپلیت را dashboard.html در نظر گرفتم
    return render(request, 'panel_app/dashboard_profile.html', context)




@login_required
def user_orders_list_view(request):
    """
    یک ویو واحد برای نمایش تمام سفارشات کاربر در تب‌های مختلف.
    """
    # ۱. دریافت تمام سفارش‌های کاربر فعلی
    user_orders = Order.objects.filter(user=request.user).order_by('-createAt')

    # ۲. دسته‌بندی سفارش‌ها بر اساس وضعیت
    current_orders = user_orders.filter(status__in=[
        OrderStatus.PENDING,
        OrderStatus.CONFIRMED,
        OrderStatus.ON_HOLD
    ])
    delivered_orders = user_orders.filter(status=OrderStatus.DELIVERED)
    cancelled_orders = user_orders.filter(status=OrderStatus.CANCELLED)
    refunded_orders = user_orders.filter(status=OrderStatus.REFUNDED)

    # ۳. آماده‌سازی context برای ارسال به تمپلیت
    context = {
        # لیستی از ۲ سفارش فعلی برای نمایش در بالای صفحه
        'top_current_orders': current_orders[:2],

        # لیست‌های کامل برای هر تب
        'current_orders_tab': current_orders,
        'delivered_orders_tab': delivered_orders,
        'cancelled_orders_tab': cancelled_orders,
        'refunded_orders_tab': refunded_orders,
    }

    return render(request, 'panel_app/orders_list.html', context)

from django.contrib import messages

@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    context = {
        'order': order
    }

    return render(request, 'panel_app/order_detail.html', context)


# p

def download_file_view(request, order_id, file_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    file_obj = get_object_or_404(File, id=file_id)

    # لینک مستقیم (مثل Google Drive)
    url = file_obj.downloadLink

    # دانلود فایل به صورت stream
    r = requests.get(url, stream=True)
    if r.status_code != 200:
        return HttpResponse("خطا در دانلود فایل", status=400)

    # تعیین نام نهایی
    filename = f"{file_obj.title}.zip"  # یا از db پسوند ذخیره کن

    response = HttpResponse(r.content, content_type="application/octet-stream")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from apps.order.models import Favorite, File


@login_required
def favorites_list(request):
    # دریافت تمام علاقه‌مندی‌های کاربر
    favorites = Favorite.objects.filter(user=request.user).select_related('file')

    # صفحه‌بندی
    paginator = Paginator(favorites, 12)  # 12 آیتم در هر صفحه
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'favorits': page_obj,
    }
    return render(request, 'panel_app/favorites.html', context)

@login_required
def delete_favorite(request, favorite_id):
    if request.method == 'POST':
        favorite = get_object_or_404(Favorite, id=favorite_id, user=request.user)
        favorite.delete()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'علاقه‌مندی با موفقیت حذف شد'})

        return redirect('favorites_list')

    return JsonResponse({'status': 'error', 'message': 'درخواست نامعتبر'})

@login_required
def delete_all_favorites(request):
    if request.method == 'POST':
        Favorite.objects.filter(user=request.user).delete()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'تمام علاقه‌مندی‌ها با موفقیت حذف شدند'})

        return redirect('favorites_list')

    return JsonResponse({'status': 'error', 'message': 'درخواست نامعتبر'})



from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from apps.user.models import CustomUser
from .forms import EditProfileForm

class Edit_profile(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(CustomUser, id=request.user.id)



        initial_data = {
            'name': user.name,
            'family': user.family,
            'email': user.email,
            'gender': user.gender,
            'birth_date': user.birth_date,
        }

        form = EditProfileForm(initial=initial_data)

        return render(request, 'panel_app/edit_profile.html', {
            'user': user,
            'customer': user,
            'form': form
        })

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(CustomUser, id=request.user.id)
        form = EditProfileForm(request.POST)
        if form.is_valid():
            has_changes = False

            if form.cleaned_data['name']:
                user.name = form.cleaned_data['name']
                has_changes = True

            if form.cleaned_data['family']:
                user.family = form.cleaned_data['family']
                has_changes = True

            if form.cleaned_data['gender']:
                user.gender = form.cleaned_data['gender']
                has_changes = True

            if form.cleaned_data['birth_date']:
                user.birth_date = form.cleaned_data['birth_date']
                has_changes = True

            if has_changes:
                user.save()
            else:
        # هیچ فیلدی پر نشده بود
                print("هیچ داده‌ای برای ذخیره‌سازی وجود ندارد")

            messages.success(request,'اطلاعات شما با موفقیت ویرایش شد','success')
            return redirect('panel:edit_profile')


        return render(request, 'panel_app/edit_profile.html', {
            'user': user,
            'customer': user,
            'form': form
        })