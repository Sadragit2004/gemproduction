# در فایل views.py برنامه file
from django.http import JsonResponse
from django.db.models import Q
from apps.file.models import File, Group,reverse

def search_suggestions(request):
    query = request.GET.get('q', '')
    suggestions = []

    if query:
        # جستجو در فایل‌ها
        file_results = File.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query),
            isActive=True
        )[:5]  # محدود کردن به 5 نتیجه

        # جستجو در گروه‌ها
        group_results = Group.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query),
            isActive=True
        )[:3]  # محدود کردن به 3 نتیجه

        # اضافه کردن فایل‌ها به پیشنهادات
        for file in file_results:
            suggestions.append({
                'type': 'file',
                'title': file.title,
                'url': file.get_absolute_url(),
                'image': file.image.url if file.image else None
            })

        # اضافه کردن گروه‌ها به پیشنهادات
        for group in group_results:
            suggestions.append({
                'type': 'group',
                'title': group.title,
                'url': reverse('file:filter_shop', kwargs={'slug': group.slug}),
                'image': group.image.url if group.image else None
            })

    return JsonResponse({'suggestions': suggestions})