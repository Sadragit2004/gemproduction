from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from apps.user.models import CustomUser
from apps.file.models import File
import uuid
import jdatetime
from khayyam import JalaliDatetime
import pytz
from apps.user.models import CustomUser
from django.utils.translation import gettext_lazy as _
import utils
from apps.course.models import Enrollment

class Base(models.Model):

    createAt = models.DateTimeField(default=timezone.now, verbose_name="تاریخ ساخته شده")
    updateAt = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    isActive = models.BooleanField(default=False, verbose_name="فعال / غیرفعال")


class OrderStatus:
    """کلاس ثابت برای وضعیت‌های سفارش"""
    PENDING = 'pending'
    PROCESSING = 'processing'
    CONFIRMED = 'confirmed'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'
    ON_HOLD = 'on_hold'

    CHOICES = [
        (PENDING, _('در انتظار پرداخت')),
        (CONFIRMED, _('تأیید شده')),
        (DELIVERED, _('تحویل داده شده')),
        (CANCELLED, _('لغو شده')),
        (ON_HOLD, _('در انتظار بررسی')),
    ]



class Order(Base):

    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='orders',verbose_name='مشتری')
    isFinally = models.BooleanField(default=False,verbose_name='نهایی شده')
    orderCode = models.UUIDField(unique=True,default=uuid.uuid4,verbose_name='کد سفارش',editable=False)
    discount = models.IntegerField(blank=True,null=True,default=0,verbose_name='تخفیف روی فاکتور')
    description = models.TextField(verbose_name='توضیحات',blank=True,null=True)
    status = models.CharField(
            max_length=20,
            choices=OrderStatus.CHOICES,
            default=OrderStatus.PENDING,
            verbose_name='وضعیت سفارش'
        )

    @property
    def status_info(self):
        """
        یک دیکشنरी شامل جزئیات کامل وضعیت سفارش برای استفاده در تمپلیت برمی‌گرداند.
        """
        # تعریف آیکون‌ها و درصد پیشرفت برای هر وضعیت
        status_details = {
            OrderStatus.PENDING: {'icon': 'order-current', 'percent': 25},
            OrderStatus.CONFIRMED: {'icon': 'order-current', 'percent': 50},
            OrderStatus.DELIVERED: {'icon': 'order-delivered', 'percent': 100},
            OrderStatus.CANCELLED: {'icon': 'order-canceled', 'percent': 0},
            OrderStatus.ON_HOLD: {'icon': 'order-current', 'percent': 40},
            OrderStatus.REFUNDED: {'icon': 'order-returned', 'percent': 0},
        }

        # دریافت جزئیات وضعیت فعلی یا یک مقدار پیش‌فرض
        details = status_details.get(self.status, {'icon': 'question-mark-circle', 'percent': 0})

        svg_code = f'<svg class="h-6 w-6"><use xlink:href="#{details["icon"]}"></use></svg>'

        return {
            'title_status': self.get_status_display(),
            'svg_stutus': svg_code,
            'percent_develop': details['percent'] # کلید جدید برای نوار پیشرفت
        }

    def get_jalali_createAt(self):
    # فقط تاریخ جلالی بازگردانده می‌شود
        return JalaliDatetime(self.createAt).strftime('%Y/%m/%d')


    def get_order_total_price(self):
        sum = 0
        for item in self.orders_details.all():
            # اگر فایل دارد
            if item.files:
                sum += item.files.get_price_by_discount()
            # اگر دوره دارد
            elif item.enrollment:
                sum += item.enrollment.course.totalPrice
        finaly_total_price, tax = utils.price_by_delivery_tax(sum, self.discount)
        return int(finaly_total_price * 10)



    # def createAt_in_iran(self):
    #     tehran_tz = pytz.timezone('Asia/Tehran')
    #     return self.createAt.astimezone(tehran_tz)

    def get_discounted_amount(self):
    # قیمت کل سفارش قبل از تخفیف
        initial_total_price = 0
        for item in self.orders_details.all():
            # اگر فایل دارد
            if item.files:
                initial_total_price += item.files.price
            # اگر دوره دارد
            elif item.enrollment:
                initial_total_price += item.enrollment.course.totalPrice

        # قیمت کل سفارش بعد از تخفیف
        finaly_total_price, tax = utils.price_by_delivery_tax(initial_total_price, self.discount)

        # اگر قیمت نهایی از قیمت اولیه بیشتر شد یا تخفیف نداشتیم، تخفیف را 0 بگذاریم
        if finaly_total_price >= initial_total_price or self.discount == 0:
            return 0

        # محاسبه تخفیف خورده به تومان
        discounted_amount = (initial_total_price - finaly_total_price) * 10

        # تبدیل تخفیف به هزار تومان
        discounted_amount_in_thousands = int(discounted_amount / 1000)

        return discounted_amount_in_thousands




    def save(self, *args, **kwargs):
        tehran_tz = pytz.timezone('Asia/Tehran')
        if self.createAt:
            self.createAt = self.createAt.astimezone(tehran_tz)
        super().save(*args, **kwargs)



    def is_paid(self):
        """بررسی آیا سفارش پرداخت شده است"""
        # استفاده از مقادیر از کلاس OrderStatus
        paid_statuses = [OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.DELIVERED]
        return self.status in paid_statuses and self.isFinally



    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارشات'

# =================================================

class OrderDetail(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='orders_details',verbose_name='سفارش')
    files = models.ForeignKey(File,on_delete=models.CASCADE,verbose_name='محصول',related_name='orders_details_file',blank=True,null=True)
    price = models.IntegerField(verbose_name='قیمت کالا در فاکتور')
    enrollment = models.ForeignKey(Enrollment,on_delete=models.CASCADE,verbose_name='دوره',null=True,blank=True)



    # def __str__(self) -> str:
    #     return f'{self.order}\t{self.file}\t{self.qty}\t{self.price}'

# =================================================

# در فایل models.py مربوط به فایل/محصولات

class Favorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="کاربر", related_name="favorites")
    file = models.ForeignKey(File, on_delete=models.CASCADE, verbose_name="فایل", related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "علاقه‌مندی"
        verbose_name_plural = "علاقه‌مندی‌ها"
        unique_together = ('user', 'file')  # جلوگیری از اضافه کردن تکراری

    def __str__(self):
        return f"{self.user.mobileNumber} - {self.file.title}"