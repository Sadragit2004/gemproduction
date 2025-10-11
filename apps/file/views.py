from django.shortcuts import render,get_object_or_404
from django.db.models import Q,Count,Min,Max
from django.views.decorators.cache import cache_page
from .models import File, Group
from apps.order.models import Favorite
from django.core.paginator import Paginator
from django.http import JsonResponse
from apps.file.models import File
from .models import Comment,Group
from django.conf import settings # برای دسترسی به MEDIA_URL
from django.contrib.auth.decorators import login_required
import json
from django.views import View
from django.template.loader import render_to_string
from .filters import ProductFilter
from apps.discount.models import Discount_detail

def file_list_view(request, template_name, order_by_field):
    files = File.objects.filter(isActive=True).order_by(order_by_field)[:10]
    return render(request, template_name, {"files": files})


def latest_files(request):
    return file_list_view(request, "files_app/latest_files.html", "-createAt")


def expensive_files(request):
    return file_list_view(request, "files_app/expensive_files.html", "-price")


def rich_groups(request):
    groups = Group.objects.annotate(file_count=Count("files_of_groups")).order_by("-file_count")[:8]
    return render(request, "files_app/rich_groups.html", {"groups": groups})





def speciel_sale(request):


    basket_things = Discount_detail.objects.all()
    return render(request,'files_app/special_sale.html',{'baskets':basket_things})


def file_group_view(request):
    # فقط گروه‌های اصلی (بدون والد) را فیلتر کن
    groups = Group.objects.filter(parent__isnull=True).prefetch_related('groups__groups')
    context = {
        'groups': groups
    }

    return render(request, 'files_app/gatigoeary_group_header.html', context)





def best_selling_files(request):

    files = (
        File.objects.annotate(order_count=Count('orders_details_file'))
        .filter(order_count__gt=0)
        .order_by('-order_count')[:10]
    )

    context = {
        'files': files
    }
    return render(request, 'files_app/best_selling_files.html', context)



@cache_page(0 * 0)
def file_detail(request, slug):
    file_obj = get_object_or_404(File, slug=slug, isActive=True)
    is_favorited = False
    if request.user.is_authenticated:
            is_favorited = Favorite.objects.filter(user=request.user, file=file_obj).exists()

    return render(request, 'files_app/file_detail.html', {'file': file_obj,'is_favorited': is_favorited,})


def related_products(request, *args, **kwargs):
    try:
        current_product = get_object_or_404(File, slug=kwargs['slug'], isActive=True)

        related_products = []
        for group in current_product.group.all():
            related_products.extend(File.objects.filter(
                Q(isActive=True) &
                Q(group=group) &
                ~Q(id=current_product.id)
            ))

        related_products = list(set(related_products))


        context = {
            'current_product': current_product,
            'related_products': related_products
        }
        return render(request, 'files_app/related_product.html', context)

    except Exception as e:
        # اگر خطا شد، حداقل یه رندر خالی برگردون
        return render(request, 'files_app/related_product.html', {
            'current_product': None,
            'related_products': []
        })






def group_in_category(request,*args, **kwargs):
    products_group =  Group.objects.annotate(count = Count('files_of_groups'))\
        .filter(Q(isActive = True) & ~Q(count = 0)).order_by('-count')


    return render(request,'files_app/shop/group_in_category.html',{'groups':products_group})




@login_required

def save_comment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # دریافت داده‌ها
            file_id = data.get('file_id')
            text = data.get('text')
            is_suggest = data.get('is_suggest', True)  # پیشنهاد میکنم = True

            # اعتبارسنجی
            if not text or not file_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'لطفا متن دیدگاه را وارد کنید'
                }, status=400)

            # ایجاد کامنت
            comment = Comment.objects.create(
                user=request.user,
                file_id=file_id,
                text=text,
                is_suggest=is_suggest,
                is_active=False  # منتظر تایید ادمین
            )

            return JsonResponse({
                'status': 'success',
                'message': 'دیدگاه شما با موفقیت ثبت شد و پس از تایید نمایش داده می‌شود',
                'comment_id': comment.id
            })

        except File.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'محصول یافت نشد'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': 'خطا در ثبت دیدگاه'
            }, status=500)

    return JsonResponse({'status': 'error', 'message': 'روش ارسال نامعتبر'}, status=405)

def get_feature_filter(request, *args, **kwargs):
    slug = kwargs['slug']
    group_product = get_object_or_404(Group, slug=slug)

    # گرفتن ویژگی‌های مرتبط با این گروه
    feature_list = group_product.features.all()

    feature_dict = {}
    for feature in feature_list:
        feature_dict[feature] = feature.feature_values.all()

    # ویژگی‌های انتخاب‌شده توسط کاربر
    selected_features = request.GET.getlist("feature")

    context = {
        'feature_dict': feature_dict,
        'group': group_product,
        'selected_features': selected_features,  # 🔹 اینو پاس بده
    }
    return render(request, 'files_app/shop/feature_list_filer.html', context)



def show_by_filter(request, *args, **kwargs):
    slug = kwargs['slug']
    group = get_object_or_404(Group, slug=slug)
    # تمام فایل‌های فعال در این گروه را دریافت می‌کنیم
    base_files = File.objects.filter(Q(isActive=True) & Q(group=group))
    result_price = base_files.aggregate(max=Max('price'), min=Min('price'))

    # مقدار انتخاب‌شده توسط کاربر (اگر وجود داشت)
    selected_price = request.GET.get("price")

    # اعمال فیلترهای اولیه از django-filter
    filter = ProductFilter(request.GET, queryset=base_files)
    files = filter.qs

    # اگر کاربر قیمت انتخاب کرده بود، روی queryset هم فیلتر بشه
    if selected_price:
        try:
            selected_price = int(selected_price)
            files = files.filter(price__lte=selected_price)
        except ValueError:
            selected_price = None

    # اعمال فیلتر بر اساس ویژگی‌ها (features)
    feature_filter = request.GET.getlist('feature')
    if feature_filter:
        files = files.filter(
            features_value__filterValue__id__in=feature_filter
        ).distinct()

    # اعمال مرتب‌سازی
    sort = request.GET.get('sort')
    if sort == '1':
        files = files.order_by('-createAt')
    elif sort == '3':
        files = files.order_by('price')
    elif sort == '2':
        files = files.order_by('-price')
    elif sort == '4':
        # TODO: implement best-selling sorting
        pass
    else:
        files = files.order_by('-createAt')

    # --- شروع منطق صفحه‌بندی ---
    paginator = Paginator(files, 6)  # هر صفحه ۶ آیتم
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # اگر درخواست از نوع AJAX باشد (برای دکمه "نمایش بیشتر")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string(
            'files_app/shop/files_loop.html',
            {
                'files': page_obj,
                'media_url': settings.MEDIA_URL
            }
        )
        return JsonResponse({'html': html, 'has_next': page_obj.has_next()})
    # --- پایان منطق صفحه‌بندی ---

    context = {
        'files': page_obj,
        'result_price': result_price,
        'slug': slug,
        'group': group,
        'selected_price': selected_price or result_price["max"],  # برای نمایش درست اسلایدر
    }
    return render(request, 'files_app/shop/shop.html', context)
