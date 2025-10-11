from django.db import models
from apps.user.models import CustomUser
import uuid

# Create your models here.

# =========================
# Ticket System Models
# =========================

class TicketDepartment(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام دپارتمان")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "دپارتمان تیکت"
        verbose_name_plural = "دپارتمان‌های تیکت"

    def __str__(self):
        return self.name


class TicketPriority(models.Model):
    name = models.CharField(max_length=50, verbose_name="اولویت")
    color = models.CharField(max_length=7, default="#000000", verbose_name="رنگ")
    order = models.IntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "اولویت تیکت"
        verbose_name_plural = "اولویت‌های تیکت"
        ordering = ['order']

    def __str__(self):
        return self.name


class TicketStatus(models.Model):
    name = models.CharField(max_length=50, verbose_name="وضعیت")
    color = models.CharField(max_length=7, default="#000000", verbose_name="رنگ")
    is_closed = models.BooleanField(default=False, verbose_name="وضعیت بسته شده")

    class Meta:
        verbose_name = "وضعیت تیکت"
        verbose_name_plural = "وضعیت‌های تیکت"

    def __str__(self):
        return self.name


class Ticket(models.Model):
    ticket_id = models.CharField(max_length=20, unique=True, verbose_name="شماره تیکت")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="tickets", verbose_name="کاربر")
    department = models.ForeignKey(TicketDepartment, on_delete=models.SET_NULL, null=True, verbose_name="دپارتمان")
    priority = models.ForeignKey(TicketPriority, on_delete=models.SET_NULL, null=True, verbose_name="اولویت")
    status = models.ForeignKey(TicketStatus, on_delete=models.SET_NULL, null=True, verbose_name="وضعیت")
    subject = models.CharField(max_length=200, verbose_name="موضوع")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")
    is_read_user = models.BooleanField(default=True, verbose_name="خوانده شده توسط کاربر")
    is_read_admin = models.BooleanField(default=False, verbose_name="خوانده شده توسط ادمین")

    class Meta:
        verbose_name = "تیکت"
        verbose_name_plural = "تیکت‌ها"
        ordering = ['-updated_at']

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            self.ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_id} - {self.subject}"


class TicketMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="messages", verbose_name="تیکت")
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="فرستنده")
    message = models.TextField(verbose_name="پیام")
    file = models.FileField(upload_to='ticket_files/', blank=True, null=True, verbose_name="فایل")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")
    is_admin_reply = models.BooleanField(default=False, verbose_name="پاسخ ادمین")
    is_read_user = models.BooleanField(default=True, verbose_name="خوانده شده توسط کاربر")
    is_read_admin = models.BooleanField(default=True, verbose_name="خوانده شده توسط ادمی")



    class Meta:
        verbose_name = "پیام تیکت"
        verbose_name_plural = "پیام‌های تیکت"
        ordering = ['created_at']

    def __str__(self):
        return f"پیام برای {self.ticket.ticket_id}"


class TicketAssignment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="assignments", verbose_name="تیکت")
    admin_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="ادمین")
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ انتساب")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "انتساب تیکت"
        verbose_name_plural = "انتساب‌های تیکت"

    def __str__(self):
        return f"{self.ticket.ticket_id} - {self.admin_user.name}"