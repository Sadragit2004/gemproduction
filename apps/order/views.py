# apps/cart/views.py
from django.http import JsonResponse
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages
from apps.file.models import File
from apps.order.shop_cart import ShopCart
from django.views.decorators.http import require_POST
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from apps.user.models import CustomUser
from apps.order.models import Order,OrderDetail,OrderStatus
from .forms import CustomerForm
import utils
from apps.discount.forms import CopouCode
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

def add_to_cart(request, file_id):
    cart = ShopCart(request)
    file = get_object_or_404(File, id=file_id)
    cart.add(file)

    # دریافت اطلاعات به‌روز شده سبد خرید
    cart_items = cart.get_cart()
    cart_total = cart.get_total_price()

    return JsonResponse({
        "success": True,
        "count": len(cart),
        "total_price": cart_total,
        "cart_items": [
            {
                "file_id": item["file"].id,
                "title": item["title"],
                "price": str(item["price"]),
                "image": item["image"],
                "final_price": item["final_price"],
                "url": item["file"].get_absolute_url()
            }
            for item in cart_items
        ]
    })



def cart_count(request):
    cart = ShopCart(request)
    return JsonResponse({
        "count": len(cart),
        "total_price": cart.get_total_price(),
    })



def show_item(request):
    cart = ShopCart(request)
    items = cart.get_cart()
    total_price = cart.get_total_price()

    return JsonResponse({
        "success": True,
        "cart_total": total_price,
        "cart_count": len(cart),
        "cart_items": [
            {
                "file_id": item["file"].id,
                "title": item["title"],
                "price": str(item["price"]),
                "final_price": item["final_price"],
                "image": item["image"],
                "url": item["file"].get_absolute_url()
            }
            for item in items
        ]
    })



@csrf_exempt
@require_POST
def remove_from_cart(request, file_id):
    cart = ShopCart(request)
    file = get_object_or_404(File, id=file_id)
    cart.remove(file)

    # دریافت اطلاعات به‌روز شده سبد خرید
    cart_items = cart.get_cart()
    cart_total = cart.get_total_price()

    return JsonResponse({
        "success": True,
        "count": len(cart),
        "total_price": cart_total,
        "cart_items": [
            {
                "file_id": item["file"].id,
                "title": item["title"],
                "price": str(item["price"]),
                 "final_price": item["final_price"],
                "image": item["image"],
                "url": item["file"].get_absolute_url()
            }
            for item in cart_items
        ]
    })




def get_cart_org(request):
    """
    نمایش صفحه سبد خرید
    """
    cart = ShopCart(request)

    # تعداد کالا
    count = len(cart)

    # مجموع قیمت‌ها
    total_price = cart.get_total_price()

    # مالیات (مثال: 9%)
    tax_rate = Decimal("0.09")
    tax = (total_price * tax_rate).quantize(Decimal("1"))



    # مبلغ نهایی
    finaly_price = total_price + tax

    context = {
        "shop_cart": cart,
        "count": count,
        "total_price": total_price,
        "tax": tax,

        "finaly_price": finaly_price,
        "media_url": settings.MEDIA_URL,
    }

    return render(request, "order_app/cart/shop_cart.html", context)


class CreateOrderView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        shop_cart = ShopCart(request)

        if len(shop_cart.cart) > 0:
            # ساخت سفارش جدید با استفاده مستقیم از request.user
            order = Order.objects.create(
                user=request.user,  # استفاده مستقیم از request.user
                status=OrderStatus.PENDING
            )

            # اضافه کردن جزئیات سفارش
            for item in shop_cart:
                OrderDetail.objects.create(
                    order=order,
                    files=item['file'],
                    price=item['price'],
                )

            messages.success(request, "سفارش شما با موفقیت ایجاد شد و در انتظار پرداخت است.")
            return redirect('order:CheckOrder',order.id)

        else:
            messages.error(request, "شما کالایی در سبد خرید خود ثبت نکردید.", "danger")
            return redirect("main:index")




class CheckOutOrder(LoginRequiredMixin,View):

    def get(self,request,order_id,*args, **kwargs):


        user = request.user

        shop_cart = ShopCart(request)
        order = get_object_or_404(Order,id = order_id)

        total_price = shop_cart.get_total_price()
        finaly_total_price,tax = utils.price_by_delivery_tax(total_price,order.discount)


        data = {
            'name':user.name,
            'family':user.family,
            'email':user.email,
        }

        form = CustomerForm(data)
        form_copon = CopouCode()


        order.save()

        context = {

            'shop_cart':shop_cart,
            'total_price':total_price,
            'tax':tax,
            'order_final_price':finaly_total_price,
            'form':form,
            'count':len(shop_cart.cart),
            'form_copon':form_copon,
            'order_id':order.id,


        }


        return render(request,'order_app/checkout.html',context)



    def post(self,request,order_id,*args, **kwargs):
        form = CustomerForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data


            try:

                user = CustomUser.objects.get(id = request.user.id)


                order = Order.objects.get(id = order_id)
                order.description = data['descript']
                # order.peyment_mode = PeymentType.objects.get(id = data['peyment_type'])
                order.save()

                user.name = data['name']
                user.family = data['family']

                user.save()

                messages.success(request,'اطلاعات شما بروزرسانی شد','success')
                return redirect('order:CheckOrder',order_id)


            except :
                messages.error(request,'فاکتوری با این مشخصات یافت نشد','danger')
                return redirect('order:CheckOrder',order_id)


        messages.error(request,'اطلاعات وارد شده نامعتبر است','danger')
        return redirect('order:CheckOrder',order_id)



from apps.discount.models import Copon
from django.db.models import Q,Count,Min,Max

class ApplyCopon(View):
    def post(self, request, *args, **kwargs):
        order_id = kwargs['order_id']
        copon_form = CopouCode(request.POST)

        if copon_form.is_valid():
            code = copon_form.cleaned_data['coupon_code']

            copon = Copon.objects.filter(
                Q(Copon=code) &
                Q(isActive=True) &
                Q(start_date__lte=timezone.now()) &
                Q(end_date__gte=timezone.now())
            ).first()  # فقط یکی بگیر

            discount = 0
            try:
                order = Order.objects.get(id=order_id)
                if copon:
                    discount = copon.discount
                    order.discount = discount
                    order.save()
                    messages.success(request, 'اعمال کوپن با موفقیت انجام شد')
                else:
                    order.discount = discount
                    order.save()
                    messages.error(request, 'کد وارد شده معتبر نیست')

            except Order.DoesNotExist:
                messages.error(request, 'سفارش شما موجود نیست')

        return redirect('order:CheckOrder', order_id)

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import Favorite, File

@require_POST
def toggle_favorite(request, file_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'ابتدا وارد شوید'}, status=401)

    file = get_object_or_404(File, id=file_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, file=file)

    if not created:
        favorite.delete()
        return JsonResponse({'status': 'removed', 'is_favorited': False})

    return JsonResponse({'status': 'added', 'is_favorited': True})
