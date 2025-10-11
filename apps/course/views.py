# your_app/views.py

from django.shortcuts import render
from django.db.models import Count, Avg, F, Q
from django.db.models.functions import Coalesce
from .models import Course

def main_course(request):
    """
    دو لیست مجزا از دوره‌های "محبوب‌ترین" و "جدیدترین" را
    برای نمایش در تمپلیت آماده می‌کند.
    """
    # کوئری پایه برای جلوگیری از تکرار کد
    base_qs = Course.objects.prefetch_related(
        'enrollments', 'ratings', 'comments', 'videos'
    ) # برای مثال، فقط دوره‌های فعال را نشان می‌دهیم

    # 1. تهیه لیست "جدیدترین" دوره‌ها
    # دوره‌ها بر اساس تاریخ ایجاد مرتب شده و ۸ مورد اول انتخاب می‌شوند.
    newest_courses = base_qs.order_by('-createdAt')[:8]

    # 2. تهیه لیست "محبوب‌ترین" دوره‌ها
    # ابتدا دوره‌ها با متریک‌های محبوبیت annotate شده، سپس مرتب و ۸ مورد اول انتخاب می‌شوند.
    popular_courses = base_qs.annotate(
        num_students=Count('enrollments', filter=Q(enrollments__isActive=True), distinct=True),
        avg_rating=Coalesce(Avg('ratings__rating'), 0.0)
    ).annotate(
        # محاسبه امتیاز محبوبیت (وزن‌ها قابل تنظیم است)
        popularity_score=(F('avg_rating') * 0.7) + (F('num_students') * 0.3)
    ).order_by('-popularity_score', '-createdAt')[:8]

    # آماده‌سازی context با دو کلید مجزا برای ارسال به تمپلیت
    context = {
        'newest_courses': newest_courses,
        'popular_courses': popular_courses,
    }

    # رندر کردن تمپلیت با context
    return render(request, 'course_app/course.html', context)




from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, Count
import json
from .models import Course, Video, CourseComment, CourseRating, CourseCategoryRelation, Enrollment, InstructorProfile
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)

    # اطلاعات استاد
    try:
        instructor_profile = InstructorProfile.objects.get(user=course.instructor)
    except InstructorProfile.DoesNotExist:
        instructor_profile = None

    # ویدیوهای دوره
    videos = Video.objects.filter(course=course).order_by('order')

    # نظرات تایید شده
    comments = CourseComment.objects.filter(course=course, isApproved=True).order_by('-createdAt')

    # دسته‌بندی‌های دوره
    categories_relations = CourseCategoryRelation.objects.filter(course=course)
    categories = [rel.category for rel in categories_relations]

    # دوره‌های مرتبط (از طریق دسته‌بندی مشترک)
    related_courses = Course.objects.filter(
        categories__category__in=categories
    ).exclude(id=course.id).distinct()[:3]

    # محاسبه امتیاز متوسط
    rating_stats = CourseRating.objects.filter(course=course).aggregate(
        avg_rating=Avg('rating'),
        total_ratings=Count('id')
    )

    # بررسی آیا کاربر لاگین کرده امتیاز داده یا نه
    user_rating = None
    if request.user.is_authenticated:
        try:
            user_rating = CourseRating.objects.get(course=course, user=request.user)
        except CourseRating.DoesNotExist:
            pass

    # بررسی آیا کاربر در دوره ثبت نام کرده
    enrollment = None
    is_enrolled = False
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(
            user=request.user,
            course=course
        ).first()
        is_enrolled = enrollment is not None

    context = {
        'course': course,
        'instructor_profile': instructor_profile,
        'instructor': course.instructor,
        'videos': videos,
        'comments': comments,
        'categories': categories,
        'related_courses': related_courses,
        'avg_rating': round(rating_stats['avg_rating'] or 0, 1),
        'total_ratings': rating_stats['total_ratings'] or 0,
        'user_rating': user_rating.rating if user_rating else None,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,  # اضافه شده
        'student_count': course.studentCount,
        'total_hours': course.totalHoursHuman,
    }

    return render(request, 'course_app/course_detail.html', context)

@csrf_exempt
@require_POST
def submit_rating(request, course_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'لطفا ابتدا وارد شوید'})

    try:
        data = json.loads(request.body)
        score = int(data.get('score'))

        if score < 1 or score > 5:
            return JsonResponse({'success': False, 'error': 'امتیاز باید بین 1 تا 5 باشد'})

        course = get_object_or_404(Course, id=course_id)

        # بروزرسانی یا ایجاد امتیاز جدید
        rating, created = CourseRating.objects.update_or_create(
            course=course,
            user=request.user,
            defaults={'rating': score}
        )

        # محاسبه امتیاز جدید
        rating_stats = CourseRating.objects.filter(course=course).aggregate(
            avg_rating=Avg('rating'),
            total_ratings=Count('id')
        )

        return JsonResponse({
            'success': True,
            'avg_rating': round(rating_stats['avg_rating'] or 0, 1),
            'total_ratings': rating_stats['total_ratings'] or 0,
            'user_rating': score
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_POST
def submit_comment(request, course_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'لطفا ابتدا وارد شوید'})

    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()

        if not text:
            return JsonResponse({'success': False, 'error': 'متن نظر نمی‌تواند خالی باشد'})

        course = get_object_or_404(Course, id=course_id)

        comment = CourseComment.objects.create(
            course=course,
            user=request.user,
            comment=text
        )

        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'user_name': request.user.name if hasattr(request.user, 'name') and request.user.name else request.user.username,
                'comment': comment.comment,
                'created_at': comment.createdAt.strftime('%Y-%m-%d %H:%M'),
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from .models import Enrollment, Course
from apps.user.models import CustomUser
from apps.order.models import Order, OrderDetail

class CourseEnrollmentView(LoginRequiredMixin, View):
    def post(self, request, course_id):
        # بررسی اینکه کاربر مربی نباشد
        if hasattr(request.user, 'instructorProfile'):
            return JsonResponse({
                'success': False,
                'message': 'مربیان نمی‌توانند در دوره‌ها ثبت نام کنند'
            }, status=403)

        try:
            with transaction.atomic():
                # دریافت دوره
                course = get_object_or_404(Course, id=course_id)

                # بررسی آیا کاربر قبلاً ثبت نام کرده است
                existing_enrollment = Enrollment.objects.filter(
                    user=request.user,
                    course=course
                ).first()

                if existing_enrollment:
                    if existing_enrollment.isPay:
                        return JsonResponse({
                            'success': False,
                            'message': 'شما قبلاً در این دوره ثبت نام کرده‌اید'
                        }, status=400)
                    else:
                        return JsonResponse({
                            'success': False,
                            'message': 'شما قبلاً ثبت نام کرده‌اید اما پرداخت انجام نشده است'
                        }, status=400)

                # ایجاد Enrollment با isPay=False
                enrollment = Enrollment.objects.create(
                    user=request.user,
                    course=course,
                    isActive=True,
                    isPay=False
                )

                # ایجاد Order
                order = Order.objects.create(
                    user=request.user,
                    isFinally=False,
                    discount=0,
                    description=f'ثبت نام در دوره {course.courseName}',
                )

                # ایجاد OrderDetail
                order_detail = OrderDetail.objects.create(
                    order=order,
                    enrollment=enrollment,
                    price=int(course.totalPrice * 10)  # تبدیل به تومان
                )

                # محاسبه اطلاعات مالی
                course_price = int(course.totalPrice * 10)  # قیمت دوره به تومان
                tax_rate = 9  # 9 درصد مالیات
                tax_amount = int(course_price * tax_rate / 100)
                total_amount = course_price + tax_amount

                return JsonResponse({
                    'success': True,
                    'message': 'ثبت نام با موفقیت انجام شد. لطفاً پرداخت را تکمیل کنید.',
                    'enrollment_id': str(enrollment.id),
                    'order_code': str(order.orderCode),
                    'order_id': str(order.id),
                    'course_price': course_price,
                    'tax_amount': tax_amount,
                    'total_amount': total_amount,
                    'payment_required': True
                })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'خطا در ثبت نام: {str(e)}'
            }, status=500)