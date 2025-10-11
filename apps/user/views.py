from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt
import random
from datetime import timedelta

from .forms import MobileForm, VerificationCodeForm
from .models import CustomUser, UserSecurity
import utils

import json
from django.http import JsonResponse
from utils import send_sms

# ======================
# مرحله 1: ورود شماره موبایل
# ======================
def send_mobile(request):
    next_url = request.GET.get("next")  # گرفتن next از url

    if request.method == "POST":
        form = MobileForm(request.POST)
        if form.is_valid():
            mobile = form.cleaned_data['mobileNumber']

            # بررسی وجود کاربر یا ساخت
            user, created = CustomUser.objects.get_or_create(mobileNumber=mobile)

            if created:
                user.is_active = False
                user.save()

            # مطمئن شو UserSecurity همیشه وجود داره
            security, _ = UserSecurity.objects.get_or_create(user=user)

            # تولید کد تأیید
            code = utils.create_random_code(5)
            expire_time = timezone.now() + timedelta(minutes=2)
            send_sms(mobile, code)
            security.activeCode = code
            security.expireCode = expire_time
            security.isBan = False
            security.save()

            # TODO: ارسال SMS
            print(f"📲 کد تأیید برای {mobile}: {code}")

            # ذخیره شماره موبایل و next در سشن
            request.session["mobileNumber"] = mobile
            if next_url:
                request.session["next_url"] = next_url

            return redirect("account:verify_code")

    else:
        form = MobileForm()

    return render(request, "user_app/register.html", {"form": form, "next": next_url})


# ======================
# مرحله 2: تأیید کد
# ======================
def verify_code(request):
    mobile = request.session.get("mobileNumber")
    next_url = request.session.get("next_url")

    if not mobile:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'شماره موبایل یافت نشد'})
        return redirect("account:send_mobile")


    try:
        user = CustomUser.objects.get(mobileNumber=mobile)
        security, _ = UserSecurity.objects.get_or_create(user=user)
    except CustomUser.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'کاربری با این شماره موبایل یافت نشد'})
        messages.error(request, "کاربری با این شماره موبایل یافت نشد.")
        return redirect("account:send_mobile")



    if request.method == "POST":
        # ارسال مجدد کد
        if "resend" in request.POST and request.POST["resend"] == "true":
            code = utils.create_random_code(5)
            expire_time = timezone.now() + timedelta(minutes=2)

            security.activeCode = code
            security.expireCode = expire_time
            security.isBan = False
            security.save()


            send_sms(mobile, code)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'کد جدید ارسال شد'})

            messages.success(request, "کد جدید ارسال شد ✅")
            return redirect("account:verify_code")

        # بررسی کد ارسالی
        form = VerificationCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['activeCode']

            if security.expireCode and security.expireCode < timezone.now():
                messages.error(request, "⏳ کد منقضی شده است، دوباره تلاش کنید.")
                return redirect("account:send_mobile")

            if security.activeCode != code:
                messages.error(request, "❌ کد تأیید اشتباه است.")
            else:
                user.is_active = True
                user.save()

                security.activeCode = None
                security.expireCode = None
                security.save()

                login(request, user)
                messages.success(request, "✅ ورود موفقیت‌آمیز بود.")
                return redirect(next_url or "main:index")

    else:
        form = VerificationCodeForm()

    return render(request, "user_app/verify_otp.html", {"form": form, "mobile": mobile})


# ======================
# خروج از حساب
# ======================
def user_logout(request):
    logout(request)
    messages.success(request, "✅ شما با موفقیت از حساب کاربری خارج شدید.")
    return redirect("main:index")
