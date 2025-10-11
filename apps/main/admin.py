from django.contrib import admin

# Register your models here.
from .models import Slider_site,Slider_main,MetaTagMainPage,InfoCompany
from django.utils.html import format_html
from django.utils import timezone


@admin.register(Slider_site)
class SliderSiteAdmin(admin.ModelAdmin):
    list_display = ('text_slider', 'image_preview', 'alt_slide', 'is_active', 'register_data', 'End_data')
    list_filter = ('is_active', 'register_data', 'End_data')
    search_fields = ('text_slider', 'alt_slide')

    # To display an image preview in the admin panel
    def image_preview(self, obj):
        return format_html(f'<img src="{obj.image_name.url}" style="height: 50px;"/>')

    image_preview.short_description = 'Preview'

    # Overriding the save_model to deactivate expired sliders
    def save_model(self, request, obj, form, change):
        if obj.End_data and obj.End_data < timezone.now():
            obj.is_active = False
        super().save_model(request, obj, form, change)

    # To automatically deactivate expired sliders when saving them in the admin
    def save_formset(self, request, form, formset, change):
        for form in formset.forms:
            if form.instance.End_data and form.instance.End_data < timezone.now():
                form.instance.is_active = False
        formset.save()



@admin.register(Slider_main)
class SlidermainAdmin(admin.ModelAdmin):
    list_display = ('text_slider', 'image_preview', 'alt_slide', 'is_active', 'register_data', 'End_data')
    list_filter = ('is_active', 'register_data', 'End_data')
    search_fields = ('text_slider', 'alt_slide')

    # To display an image preview in the admin panel
    def image_preview(self, obj):
        return format_html(f'<img src="{obj.image_name.url}" style="height: 50px;"/>')

    image_preview.short_description = 'Preview'

    # Overriding the save_model to deactivate expired sliders
    def save_model(self, request, obj, form, change):
        if obj.End_data and obj.End_data < timezone.now():
            obj.is_active = False
        super().save_model(request, obj, form, change)

    # To automatically deactivate expired sliders when saving them in the admin
    def save_formset(self, request, form, formset, change):
        for form in formset.forms:
            if form.instance.End_data and form.instance.End_data < timezone.now():
                form.instance.is_active = False
        formset.save()




from .models import Banner


class BannerAdmin(admin.ModelAdmin):
    list_display = ('name_banner', 'is_active', 'register_data', 'End_data', 'image_tag', 'check_expiration')
    list_filter = ('is_active', 'register_data')
    search_fields = ('name_banner',)

    def image_tag(self, obj):
        if obj.image_name:
            return format_html('<img src="{}" width="100" height="50" />'.format(obj.image_name.url))
        return "-"
    image_tag.short_description = 'Preview'

    def check_expiration(self, obj):
        obj.deactivate_if_expired()  # چک کردن تاریخ انقضا
        return not obj.is_active
    check_expiration.short_description = 'Expired?'

admin.site.register(Banner, BannerAdmin)



@admin.register(InfoCompany)
class InfoAdmin(admin.ModelAdmin):

    list_display = ('name_company',)



@admin.register(MetaTagMainPage)
class MetaTagAdmin(admin.ModelAdmin):

    list_display = ('title_header',)