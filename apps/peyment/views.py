from django.shortcuts import render, redirect
import requests
import json
from django.views import View
from django.contrib import messages
from apps.order.models import Order, OrderStatus
from apps.course.models import Enrollment
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from apps.peyment.models import Peyment
from django.conf import settings
import utils

# -----------------------------
# تنظیمات زرین پال
# -----------------------------
ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"

merchant = 'f4f735fc-f559-4f0b-a34e-c0438e9a1918'


class ZarinPal:
    ZP_API_REQUEST = ZP_API_REQUEST
    ZP_API_VERIFY = ZP_API_VERIFY
    ZP_API_STARTPAY = ZP_API_STARTPAY

    def __init__(self, merchant, call_back_url):
        self.MERCHANT = merchant
        self.callbackURL = call_back_url

    def send_request(self, amount, description, email=None, mobile=None):
        req_data = {
            "merchant_id": self.MERCHANT,
            "amount": amount,
            "callback_url": self.callbackURL,
            "description": description,
            "metadata": {"mobile": mobile, "email": email}
        }
        req_header = {
            "accept": "application/json",
            "content-type": "application/json"
        }

        req = requests.post(url=self.ZP_API_REQUEST, data=json.dumps(req_data), headers=req_header)

        if len(req.json().get('errors', {})) == 0:
            authority = req.json()['data']['authority']
            return redirect(self.ZP_API_STARTPAY.format(authority=authority))
        else:
            e_code = req.json()['errors']['code']
            e_message = req.json()['errors']['message']
            return {"message": e_message, "error_code": e_code}

    def verify(self, request, amount):
        t_status = request.GET.get('Status')
        t_authority = request.GET.get('Authority')

        if t_status == 'OK':
            req_header = {"accept": "application/json", "content-type": "application/json"}
            req_data = {
                "merchant_id": self.MERCHANT,
                "amount": amount,
                "authority": t_authority
            }

            req = requests.post(url=self.ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
            response_data = req.json()

            if len(response_data.get('errors', {})) == 0:
                t_status = response_data['data']['code']
                ref_id = response_data['data'].get('ref_id')

                if t_status == 100:
                    return {"transaction": True, "pay": True, "RefID": ref_id, "message": None}
                elif t_status == 101:
                    return {"transaction": True, "pay": False, "RefID": ref_id, "message": response_data['data'].get('message')}
                else:
                    return {"transaction": False, "pay": False, "RefID": ref_id, "message": response_data['data'].get('message')}
            else:
                e_code = response_data['errors']['code']
                e_message = response_data['errors']['message']
                return {"status": 'ok', "message": e_message, "error_code": e_code}
        else:
            return {"status": 'cancel', "message": 'transaction failed or canceled by user'}


pay = ZarinPal(merchant=merchant, call_back_url="https://gemvisioniran.com/peyment/verify/")


# -----------------------------
# شروع پرداخت
# -----------------------------
def send_request(request, order_id):
    if utils.has_internet_connection():
        user = request.user
        order = Order.objects.get(id=order_id)

        peyment = Peyment.objects.create(
            order=order,
            customer=user,
            amount=order.get_order_total_price(),
            description='پرداخت شما با زرین پال انجام شد'
        )

        request.session['peyment_session'] = {
            'order_id': order.id,
            'peyment_id': peyment.id,
        }

        response = pay.send_request(
            amount=order.get_order_total_price(),
            description='توضیحات مربوط به پرداخت',
            email="Example@test.com",
            mobile=user.mobileNumber
        )

        if isinstance(response, dict) and response.get('error_code'):
            return HttpResponse(f"Error code: {response['error_code']}, Message: {response['message']}")
        return response
    else:
        messages.error(request, 'اتصال اینترنت شما قابل تأیید نیست', 'danger')
        return redirect('main:index')


# -----------------------------
# تأیید پرداخت (Verify)
# -----------------------------
class Zarin_pal_view_verfiy(LoginRequiredMixin, View):
    def get(self, request):
        t_status = request.GET.get('Status')
        t_authority = request.GET.get('Authority')
        session_data = request.session.get('peyment_session', {})

        order_id = session_data.get('order_id')
        peyment_id = session_data.get('peyment_id')

        order = Order.objects.get(id=order_id)
        peyment = Peyment.objects.get(id=peyment_id)

        if t_status == 'OK':
            req_header = {"accept": "application/json", "content-type": "application/json"}
            req_data = {
                "merchant_id": merchant,
                "amount": order.get_order_total_price(),
                "authority": t_authority
            }

            req = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
            res_json = req.json()

            if len(res_json.get('errors', {})) == 0:
                data = res_json.get('data', {})
                t_status = data.get('code')
                ref_id = data.get('ref_id')

                if t_status in [100, 101]:
                    order.isFinally = True
                    order.status = OrderStatus.CONFIRMED
                    order.save()

                    self.update_enrollment_status(order)

                    peyment.isFinaly = True
                    peyment.statusCode = t_status
                    peyment.refId = str(ref_id) if ref_id else None
                    peyment.save()

                    return redirect('peyment:show_sucess', f'کد رهگیری شما : {ref_id}')
                else:
                    peyment.statusCode = t_status
                    peyment.save()
                    return redirect('peyment:show_verfiy_unmessage', 'تراکنش ناموفق بود')
            else:
                e_code = res_json['errors']['code']
                e_message = res_json['errors']['message']
                return JsonResponse({"status": 'ok', "message": e_message, "error_code": e_code})
        else:
            order.status = OrderStatus.CANCELLED
            order.save()
            return redirect('peyment:show_verfiy_unmessage', 'پرداخت توسط کاربر لغو شد')

    def update_enrollment_status(self, order):
        try:
            order_details = order.orders_details.filter(enrollment__isnull=False)
            for order_detail in order_details:
                if order_detail.enrollment:
                    order_detail.enrollment.isPay = True
                    order_detail.enrollment.save()
        except Exception as e:
            print(f"Error updating enrollment status: {e}")


# -----------------------------
# نمایش پیام‌ها
# -----------------------------
def show_verfiy_message(request, message):
    order = Order.objects.all()
    return render(request, 'peyment_app/peyment.html', {'message': message, 'orders': order})


def show_verfiy_unmessage(request, message):
    return render(request, 'peyment_app/unpeyment.html', {'message': message})
