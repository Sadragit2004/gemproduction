from django.db import models
from django.utils.text import slugify
import uuid
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import utils
from ckeditor_uploader.fields import RichTextUploadingField

# ======================================================================
# Abstract Base
# ======================================================================
class TimeStampedModel(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# ======================================================================
# Instructor Profile
# ======================================================================
class InstructorProfile(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="instructorProfile"
    )
    bio = models.TextField(blank=True, default='')
    fileImage = utils.FileUpload('course', 'InstructorProfile')
    image = models.ImageField(upload_to=fileImage.upload_to, blank=True, null=True)

    def __str__(self):
        return f"Instructor: {self.user.name if self.user else '---'}"

# ======================================================================
# Course Model
# ======================================================================
class Course(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    courseName = models.CharField(max_length=255)
    description = RichTextUploadingField(verbose_name='2توضیحات',config_name = 'special',blank = True)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses"
    )
    fileImage = utils.FileUpload('course', 'Course')
    image = models.ImageField(upload_to=fileImage.upload_to, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    cachedPrice = models.PositiveIntegerField(
       
        default=0,
        blank=True
    )
    # isPay = models.BooleanField(default=False, verbose_name='پرداخت شده')

    def save(self, *args, **kwargs):
        if not self.slug and self.courseName:
            base_slug = slugify(self.courseName)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # محاسبه cachedPrice اگر تنظیم نشده
        if not self.cachedPrice:
            total = sum(video.price or 0 for video in self.videos.all())
            self.cachedPrice = total

        super().save(*args, **kwargs)

    @property
    def studentCount(self):
        return self.enrollments.filter(isActive=True).count()

    @property
    def totalPrice(self):
        return self.cachedPrice if self.cachedPrice is not None else 0

    @property
    def totalMinutes(self):
        return sum(video.durationMinutes or 0 for video in self.videos.all())

    @property
    def totalHoursDecimal(self):
        return round(self.totalMinutes / 60, 2) if self.totalMinutes else 0

    @property
    def totalHoursHuman(self):
        total_minutes = self.totalMinutes or 0
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours} ساعت و {minutes} دقیقه"

    @property
    def averageRating(self):
        ratings = self.ratings.all().values_list("rating", flat=True)
        if ratings:
            return round(sum(ratings) / len(ratings), 2)
        return 0

    def __str__(self):
        return self.courseName or "---"

    class Meta:
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['instructor']),

        ]

# ======================================================================
# Video Model
# ======================================================================
class Video(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="videos"
    )
    videoName = models.CharField(max_length=255)
    durationMinutes = models.PositiveIntegerField(default=0)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    isPay = models.BooleanField(default=False, verbose_name='پرداخت شده')
    link = models.TextField(blank=True, default='')
    order = models.PositiveIntegerField(default=0)  # برای ترتیب ویدیوها

    @property
    def durationHoursDecimal(self):
        return round(self.durationMinutes / 60, 2) if self.durationMinutes else 0

    def __str__(self):
        return f"{self.videoName or '---'} ({self.durationMinutes or 0} دقیقه)"

    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['course', 'order']),
        ]

# ======================================================================
# Enrollment Model
# ======================================================================
class Enrollment(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    isActive = models.BooleanField(default=True)
    enrolledAt = models.DateTimeField(auto_now_add=True)
    isPay = models.BooleanField(default=False, verbose_name='پرداخت شده')
    class Meta:
        unique_together = ("user", "course")
        indexes = [
            models.Index(fields=['user', 'isActive']),
            models.Index(fields=['course', 'isActive']),
        ]

    def __str__(self):
        name = self.user.name if self.user else '---'
        course_name = self.course.courseName if self.course else '---'
        return f"{name} -> {course_name}"

# ======================================================================
# Course Comment Model
# ======================================================================
class CourseComment(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courseComments"
    )
    comment = models.TextField()
    isApproved = models.BooleanField(default=True)  # برای مدیریت نظرات

    def __str__(self):
        name = self.user.name if self.user else '---'
        course_name = self.course.courseName if self.course else '---'
        return f"Comment by {name} on {course_name}"

    class Meta:
        indexes = [
            models.Index(fields=['course', 'isApproved']),
        ]

# ======================================================================
# Course Rating Model
# ======================================================================
class CourseRating(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="ratings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courseRatings"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    comment = models.TextField(blank=True, default='')  # ترکیب رای و نظر

    class Meta:
        unique_together = ("course", "user")
        indexes = [
            models.Index(fields=['course', 'rating']),
        ]

    def __str__(self):
        name = self.user.name if self.user else '---'
        course_name = self.course.courseName if self.course else '---'
        return f"Rating {self.rating} by {name} for {course_name}"

# ======================================================================
# Course Category Model (جدید)
# ======================================================================
class CourseCategory(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, default='')

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# ======================================================================
# Course-Category Relationship (جدید)
# ======================================================================
class CourseCategoryRelation(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="categories"
    )
    category = models.ForeignKey(
        CourseCategory,
        on_delete=models.CASCADE,
        related_name="courses"
    )

    class Meta:
        unique_together = ("course", "category")

    def __str__(self):
        course_name = self.course.courseName if self.course else '---'
        category_name = self.category.name if self.category else '---'
        return f"{course_name} - {category_name}"