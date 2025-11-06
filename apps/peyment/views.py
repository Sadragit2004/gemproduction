from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages
import requests, json
from apps.order.models import Order, OrderStatus
from apps.peyment.models import Peyment


# -----------------------------
# تأیید پرداخت زرین پال
# -----------------------------
class Zarin_pal_view_verfiy(LoginRequiredMixin, View):
    def get(self, request):
        t_status = request.GET.get('Status')
        t_authority = request.GET.get('Authority')
        session_data = request.session.get('peyment_session', {})

        order_id = session_data.get('order_id')
        peyment_id = session_data.get('peyment_id')

        if not order_id or not peyment_id:
            messages.error(request, "داده‌ای برای پرداخت یافت نشد.")
            return redirect('main:index')

        order = get_object_or_404(Order, id=order_id)
        peyment = get_object_or_404(Peyment, id=peyment_id)

        if t_status == 'OK':
            req_header = {"accept": "application/json", "content-type": "application/json"}
            req_data = {
                "merchant_id": "f4f735fc-f559-4f0b-a34e-c0438e9a1918",
                "amount": order.get_order_total_price(),
                "authority": t_authority
            }

            req = requests.post(
                url="https://api.zarinpal.com/pg/v4/payment/verify.json",
                data=json.dumps(req_data),
                headers=req_header
            )
            res_json = req.json()

            if len(res_json.get('errors', {})) == 0:
                data = res_json.get('data', {})
                t_status = data.get('code')
                ref_id = data.get('ref_id')

                # ✅ تراکنش موفق
                if t_status in [100, 101]:
                    order.isFinally = True
                    order.status = OrderStatus.CONFIRMED
                    order.save()

                    peyment.isFinaly = True
                    peyment.statusCode = t_status
                    peyment.refId = str(ref_id)
                    peyment.save()

                    # ✅ پیام را در Session ذخیره می‌کنیم
                    request.session['success_message'] = f"پرداخت شما با موفقیت انجام شد. کد رهگیری: {ref_id}"
                    request.session['peyment_session'] = {'order_id': order.id}
                    return redirect('peyment:show_verfiy_message')

                # ❌ تراکنش ناموفق
                else:
                    peyment.statusCode = t_status
                    peyment.save()
                    request.session['error_message'] = "تراکنش ناموفق بود."
                    return redirect('peyment:show_verfiy_unmessage')

            else:
                # خطای پاسخ زرین پال
                e_message = res_json['errors']['message']
                request.session['error_message'] = e_message
                return redirect('peyment:show_verfiy_unmessage')

        else:
            # کاربر تراکنش را لغو کرده است
            order.status = OrderStatus.CANCELLED
            order.save()
            request.session['error_message'] = "پرداخت توسط کاربر لغو شد."
            return redirect('peyment:show_verfiy_unmessage')


# -----------------------------
# نمایش پیام موفقیت پرداخت
# -----------------------------
def show_verfiy_message(request):
    session_data = request.session.get('peyment_session', {})
    order_id = session_data.get('order_id')

    if not order_id:
        return redirect('main:index')

    order = get_object_or_404(Order, id=order_id)
    message = request.session.pop('success_message', 'پرداخت با موفقیت انجام شد.')

    context = {
        'message': message,
        'order': order,
        'order_id': order.id,
    }
    return render(request, 'peyment_app/peyment.html', context)


# -----------------------------
# نمایش پیام ناموفق پرداخت
# -----------------------------
def show_verfiy_unmessage(request):
    message = request.session.pop('error_message', 'پرداخت ناموفق بود.')
    return render(request, 'peyment_app/unpeyment.html', {'message': message})
