from django.contrib import admin
from django.shortcuts import get_object_or_404
from .models import Discount_basket, Discount_detail,Copon
from apps.file.models import File
# Register your models here.

@admin.register(Copon)
class CoponAdmin(admin.ModelAdmin):
    list_display = ('Copon','start_date','end_date','discount','isActive',)
    ordering = ('isActive',)


class DiscountBasketDetail(admin.TabularInline):
    model = Discount_detail
    extra = 1


@admin.register(Discount_basket)
class DiscountBasketAdmin(admin.ModelAdmin):
    list_display = ('discount_title','start_date','end_date','discount','isActive',)
    ordering = ('isActive',)
    inlines = [DiscountBasketDetail]

    # اکشن برای اضافه کردن تمام محصولات به سبد تخفیف
    actions = ['add_all_files']

    def add_all_files(self, request, queryset):
        # بررسی اینکه فقط یک سبد تخفیف انتخاب شده باشد
        if queryset.count() != 1:
            self.message_user(request, "لطفا تنها یک سبد تخفیف انتخاب کنید", level='error')
            return

        discount_basket = queryset.first()

        # اضافه کردن تمام محصولات به سبد تخفیف
        files = File.objects.all()
        for file in files:
            Discount_detail.objects.get_or_create(discountBasket=discount_basket, files=file)

        self.message_user(request, "تمام محصولات به سبد تخفیف اضافه شدند")

    add_all_files.short_description = "اضافه کردن تمام محصولات به سبد تخفیف"
