from django.contrib import admin
from django.utils.html import format_html
from .models import (
    InstructorProfile, Course, Video, Enrollment,
    CourseComment, CourseRating, CourseCategory, CourseCategoryRelation
)


# ======================================================================
# Inline Admin Classes
# ======================================================================
class VideoInline(admin.TabularInline):
    model = Video
    extra = 1
    fields = ['videoName', 'durationMinutes', 'price', 'isPay', 'order']


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    readonly_fields = ['enrolledAt']
    fields = ['user', 'isActive', 'enrolledAt']


class CourseCommentInline(admin.TabularInline):
    model = CourseComment
    extra = 0
    readonly_fields = ['createdAt']
    fields = ['user', 'comment', 'isApproved', 'createdAt']


class CourseRatingInline(admin.TabularInline):
    model = CourseRating
    extra = 0
    readonly_fields = ['createdAt']
    fields = ['user', 'rating', 'comment', 'createdAt']


class CourseCategoryRelationInline(admin.TabularInline):
    model = CourseCategoryRelation
    extra = 1


# ======================================================================
# Admin Classes
# ======================================================================
@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'image_preview', 'bio_short', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'bio']
    readonly_fields = ['id', 'createdAt', 'updatedAt']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.image.url)
        return "بدون تصویر"
    image_preview.short_description = 'تصویر'

    def bio_short(self, obj):
        return obj.bio[:50] + "..." if obj.bio and len(obj.bio) > 50 else obj.bio or "-"
    bio_short.short_description = 'بیوگرافی'

    def created_at(self, obj):
        return obj.createdAt.strftime("%Y/%m/%d")
    created_at.short_description = 'تاریخ ایجاد'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        'courseName',
        'instructor',
        'price_display',
        'student_count',
        'average_rating_display',
        'duration_display',

        'created_at'
    ]
    list_filter = ['createdAt', 'instructor']
    search_fields = ['courseName', 'description', 'instructor__username']
    readonly_fields = ['id', 'slug', 'createdAt', 'updatedAt']
    inlines = [VideoInline, EnrollmentInline, CourseCommentInline, CourseRatingInline, CourseCategoryRelationInline]

    def price_display(self, obj):
        if obj.totalPrice > 0:
            return f"{int(obj.totalPrice):,} تومان"
        return "رایگان"
    price_display.short_description = 'قیمت'

    def student_count(self, obj):
        return obj.studentCount
    student_count.short_description = 'تعداد دانشجو'

    def average_rating_display(self, obj):
        rating = obj.averageRating
        if rating == 0:
            return "بدون امتیاز"
        stars = "★" * int(rating)
        return f"{stars} {rating}"
    average_rating_display.short_description = 'امتیاز'

    def duration_display(self, obj):
        return obj.totalHoursHuman
    duration_display.short_description = 'مدت زمان'



    def created_at(self, obj):
        return obj.createdAt.strftime("%Y/%m/%d")
    created_at.short_description = 'تاریخ ایجاد'


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = [
        'videoName',
        'course',
        'duration_display',
        'price_display',
        'order',
        'created_at'
    ]
    list_filter = ['course', 'createdAt']
    search_fields = ['videoName', 'course__courseName']
    readonly_fields = ['id', 'createdAt', 'updatedAt']
    list_editable = ['order']

    def duration_display(self, obj):
        return f"{obj.durationMinutes} دقیقه"
    duration_display.short_description = 'مدت زمان'

    def price_display(self, obj):
        if obj.price > 0:
            return f"{int(obj.price):,} تومان"
        return "رایگان"
    price_display.short_description = 'قیمت'


    def created_at(self, obj):
        return obj.createdAt.strftime("%Y/%m/%d")
    created_at.short_description = 'تاریخ ایجاد'


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'course',
        'isActive',
        'enrolled_at',
        'created_at'
    ]
    list_filter = ['isActive', 'enrolledAt', 'createdAt', 'course']
    search_fields = ['user__username', 'course__courseName']
    readonly_fields = ['id', 'createdAt', 'updatedAt', 'enrolledAt']
    list_editable = ['isActive']

    def enrolled_at(self, obj):
        return obj.enrolledAt.strftime("%Y/%m/%d %H:%M")
    enrolled_at.short_description = 'تاریخ ثبت‌نام'

    def created_at(self, obj):
        return obj.createdAt.strftime("%Y/%m/%d")
    created_at.short_description = 'تاریخ ایجاد'


@admin.register(CourseComment)
class CourseCommentAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'course',
        'comment_short',
        'isApproved',
        'created_at'
    ]
    list_filter = ['isApproved', 'createdAt', 'course']
    search_fields = ['user__username', 'comment', 'course__courseName']
    readonly_fields = ['id', 'createdAt', 'updatedAt']
    list_editable = ['isApproved']

    def comment_short(self, obj):
        return obj.comment[:50] + "..." if obj.comment and len(obj.comment) > 50 else obj.comment or "-"
    comment_short.short_description = 'نظر'

    def created_at(self, obj):
        return obj.createdAt.strftime("%Y/%m/%d")
    created_at.short_description = 'تاریخ ایجاد'


@admin.register(CourseRating)
class CourseRatingAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'course',
        'rating',
        'comment_short',
        'created_at'
    ]
    list_filter = ['rating', 'createdAt', 'course']
    search_fields = ['user__username', 'comment', 'course__courseName']
    readonly_fields = ['id', 'createdAt', 'updatedAt']

    def comment_short(self, obj):
        return obj.comment[:30] + "..." if obj.comment and len(obj.comment) > 30 else obj.comment or "-"
    comment_short.short_description = 'نظر'

    def created_at(self, obj):
        return obj.createdAt.strftime("%Y/%m/%d")
    created_at.short_description = 'تاریخ ایجاد'


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'slug',
        'course_count',
        'created_at'
    ]
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'createdAt', 'updatedAt']

    def course_count(self, obj):
        return obj.courses.count()
    course_count.short_description = 'تعداد دوره‌ها'

    def created_at(self, obj):
        return obj.createdAt.strftime("%Y/%m/%d")
    created_at.short_description = 'تاریخ ایجاد'


@admin.register(CourseCategoryRelation)
class CourseCategoryRelationAdmin(admin.ModelAdmin):
    list_display = [
        'course',
        'category',
        'created_at'
    ]
    list_filter = ['category', 'createdAt']
    search_fields = ['course__courseName', 'category__name']
    readonly_fields = ['id', 'createdAt', 'updatedAt']

    def created_at(self, obj):
        return obj.createdAt.strftime("%Y/%m/%d")
    created_at.short_description = 'تاریخ ایجاد'


# ======================================================================
# Admin Site Configuration
# ======================================================================
admin.site.site_header = "پنل مدیریت آموزش آنلاین"
admin.site.site_title = "آموزش آنلاین"
admin.site.index_title = "خوش آمدید به پنل مدیریت"