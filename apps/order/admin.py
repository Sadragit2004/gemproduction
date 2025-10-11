# apps/order/admin.py
from django.contrib import admin, messages
from django.http import HttpResponse
from django.utils.html import format_html
from django.urls import reverse
from django.db import transaction
import csv
from .models import Order, OrderDetail, OrderStatus


# ----- Inline برای نمایش آیتم‌های سفارش -----
class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 0
    readonly_fields = ("file_link", "price_display")
    fields = ("files", "file_link", "price", "price_display")
    autocomplete_fields = ("files",)
    raw_id_fields = ("files",)

    def file_link(self, obj):
        if not obj.files_id:
            return "-"
        url = reverse("admin:file_file_change", args=(obj.files_id,))
        return format_html('<a href="{}" target="_blank">{}</a>', url, obj.files.title)
    file_link.short_description = "محصول (لینک)"

    def price_display(self, obj):
        if obj.price is None:
            return "-"
        return f"{obj.price:,} تومان"


# ----- فیلتر وضعیت -----
class OrderStatusFilter(admin.SimpleListFilter):
    title = "وضعیت سفارش"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return OrderStatus.CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


# ----- اکشن‌ها -----
def export_orders_csv(modeladmin, request, queryset):
    """خروجی CSV برای سفارشات انتخاب‌شده"""
    field_names = ["orderCode", "user", "status", "isFinally", "createAt", "updateAt", "discount"]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=orders.csv'
    writer = csv.writer(response)
    writer.writerow(field_names)

    for obj in queryset.select_related("user"):
        row = [
            str(obj.orderCode),
            str(obj.user),
            obj.get_status_display(),
            "بله" if obj.isFinally else "خیر",
            obj.get_jalali_createAt(),
            obj.updateAt,
            obj.discount or 0
        ]
        writer.writerow(row)
    return response
export_orders_csv.short_description = "خروجی CSV از سفارش‌ها"

@admin.action(description="علامت‌گذاری به عنوان ارسال‌شده (Shipped)")
def mark_as_shipped(modeladmin, request, queryset):
    with transaction.atomic():
        updated = queryset.exclude(status=OrderStatus.SHIPPED).update(status=OrderStatus.SHIPPED)
    modeladmin.message_user(request, f"{updated} سفارش به وضعیت ارسال‌شده تغییر یافت.", messages.SUCCESS)

@admin.action(description="لغو سفارش‌ها (Cancelled)")
def cancel_orders(modeladmin, request, queryset):
    with transaction.atomic():
        updated = queryset.exclude(status=OrderStatus.CANCELLED).update(status=OrderStatus.CANCELLED)
    modeladmin.message_user(request, f"{updated} سفارش لغو شد.", messages.WARNING)


# ----- Admin برای Order -----
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderDetailInline]
    list_display = (
        "short_order_code", "user_link", "status", "isFinally",
        "total_price_display", "get_jalali_createAt", "updateAt"
    )
    list_filter = (OrderStatusFilter, "isFinally", "createAt", "updateAt")
    search_fields = ("orderCode", "user__email", "user__username", "orders_details__files__title")
    readonly_fields = ("orderCode", "createAt", "updateAt", "total_price_display", "discounted_amount_display")
    list_select_related = ("user",)
    actions = [export_orders_csv, mark_as_shipped, cancel_orders]
    date_hierarchy = "createAt"
    ordering = ("-createAt",)
    list_per_page = 25
    save_on_top = True

    fieldsets = (
        (None, {
            "fields": ("orderCode", "user", "isFinally", "status")
        }),
        ("هزینه و تخفیف", {
            "fields": ("discount", "total_price_display", "discounted_amount_display"),
        }),
        ("توضیحات", {
            "fields": ("description",)
        }),
        ("تاریخ‌ها", {
            "fields": ("createAt", "updateAt")
        }),
    )

    autocomplete_fields = ("user",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user").prefetch_related("orders_details__files")

    def short_order_code(self, obj):
        url = reverse("admin:order_order_change", args=(obj.pk,))
        return format_html('<a href="{}" title="باز کردن سفارش">{}</a>', url, str(obj.orderCode)[:8])
    short_order_code.short_description = "کد سفارش"

    def user_link(self, obj):
        if not obj.user_id:
            return "-"
        url = reverse("admin:user_customuser_change", args=(obj.user_id,))
        return format_html('<a href="{}" target="_blank">{}</a>', url, obj.user)
    user_link.short_description = "مشتری"

    def total_price_display(self, obj):
        try:
            return f"{obj.get_order_total_price():,} تومان"
        except Exception:
            return "-"
    total_price_display.short_description = "جمع فاکتور"

    def discounted_amount_display(self, obj):
        try:
            return f"{obj.get_discounted_amount():,} هزار تومان"
        except Exception:
            return "-"
    discounted_amount_display.short_description = "تخفیف"


# ----- Admin برای OrderDetail -----
@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ("order", "files", "price")
    search_fields = ("order__orderCode", "files__title")
    raw_id_fields = ("order", "files")
    list_select_related = ("order", "files")
