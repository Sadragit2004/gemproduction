# apps/ticket/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, Http404
from django.db.models import Q
from django.utils import timezone
from .models import Ticket, TicketMessage, TicketDepartment, TicketStatus, TicketAssignment
from .forms import TicketForm, TicketMessageForm

# =========================
# Decorator برای بررسی superuser
# =========================
def superuser_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise Http404("شما دسترسی به این صفحه را ندارید")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# =========================
# User Views
# =========================

@login_required
def ticket_list(request):
    tickets = Ticket.objects.filter(user=request.user).select_related(
        'department', 'priority', 'status'
    ).prefetch_related('messages').order_by('-updated_at')

    stats = {
        'total': tickets.count(),
        'open': tickets.filter(status__is_closed=False).count(),
        'closed': tickets.filter(status__is_closed=True).count(),
        'unread': tickets.filter(is_read_user=False).count(),
    }

    context = {
        'tickets': tickets,
        'stats': stats,
    }
    return render(request, 'ticket_app/ticket_list.html', context)

@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user

            # تنظیم وضعیت پیش‌فرض
            default_status = TicketStatus.objects.filter(is_closed=False).first()
            if default_status:
                ticket.status = default_status

            ticket.save()

            # ایجاد اولین پیام
            message_text = request.POST.get('initial_message', '')
            if message_text:
                TicketMessage.objects.create(
                    ticket=ticket,
                    sender=request.user,
                    message=message_text,
                    is_admin_reply=False
                )

            return redirect('ticket:ticket_detail', ticket_id=ticket.ticket_id)
    else:
        form = TicketForm()

    context = {
        'form': form,
    }
    return render(request, 'ticket_app/create_ticket.html', context)

@login_required
def ticket_detail(request, ticket_id):
    try:
        ticket = get_object_or_404(Ticket, ticket_id=ticket_id, user=request.user)
    except Ticket.DoesNotExist:
        raise Http404("تیکت مورد نظر یافت نشد")

    if request.method == 'POST':
        form = TicketMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.ticket = ticket
            message.sender = request.user
            message.is_admin_reply = False
            message.save()

            # بروزرسانی وضعیت تیکت
            ticket.is_read_admin = False
            ticket.updated_at = timezone.now()
            ticket.save()

            return redirect('ticket:ticket_detail', ticket_id=ticket_id)
    else:
        form = TicketMessageForm()

    context = {
        'ticket': ticket,
        'form': form,
        'messages': ticket.messages.all().order_by('created_at'),
    }
    return render(request, 'ticket_app/ticket_detail.html', context)

# =========================
# Admin Views - فقط برای superuserها
# =========================

@login_required
@superuser_required
def admin_dashboard(request):
    # آمار کلی
    stats = {
        'total_tickets': Ticket.objects.count(),
        'open_tickets': Ticket.objects.filter(status__is_closed=False).count(),
        'unread_tickets': Ticket.objects.filter(is_read_admin=False).count(),
        'assigned_to_me': Ticket.objects.filter(
            assignments__admin_user=request.user,
            assignments__is_active=True,
            status__is_closed=False
        ).count(),
        'closed_tickets': Ticket.objects.filter(status__is_closed=True).count(),
    }

    # فیلترها
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    department_filter = request.GET.get('department', '')
    view_filter = request.GET.get('view', 'all')
    search_query = request.GET.get('search', '')

    # پایه‌ی کوئری
    tickets = Ticket.objects.all().select_related(
        'user', 'department', 'priority', 'status'
    ).prefetch_related('messages', 'assignments').order_by('-updated_at')

    # اعمال فیلترها
    if search_query:
        tickets = tickets.filter(
            Q(ticket_id__icontains=search_query) |
            Q(subject__icontains=search_query) |
            Q(user__name__icontains=search_query) |
            Q(user__family__icontains=search_query) |
            Q(user__mobileNumber__icontains=search_query)
        )

    if status_filter:
        tickets = tickets.filter(status__name=status_filter)

    if priority_filter:
        tickets = tickets.filter(priority__name=priority_filter)

    if department_filter:
        tickets = tickets.filter(department_id=department_filter)

    if view_filter == 'unread':
        tickets = tickets.filter(is_read_admin=False)
    elif view_filter == 'assigned':
        tickets = tickets.filter(assignments__admin_user=request.user, assignments__is_active=True)
    elif view_filter == 'unassigned':
        tickets = tickets.filter(assignments__is_active=False)

    departments = TicketDepartment.objects.filter(is_active=True)

    context = {
        'stats': stats,
        'tickets': tickets,
        'departments': departments,
    }
    return render(request, 'ticket_app/admin_dashboard.html', context)

@login_required
@superuser_required
def admin_ticket_detail(request, ticket_id):
    try:
        ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    except Ticket.DoesNotExist:
        raise Http404("تیکت مورد نظر یافت نشد")

    if request.method == 'POST':
        form = TicketMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.ticket = ticket
            message.sender = request.user
            message.is_admin_reply = True
            message.save()

            # انتساب تیکت به ادمین فعلی
            if not TicketAssignment.objects.filter(ticket=ticket, is_active=True).exists():
                TicketAssignment.objects.create(
                    ticket=ticket,
                    admin_user=request.user
                )

            # بروزرسانی وضعیت تیکت
            ticket.is_read_user = False
            ticket.is_read_admin = True
            ticket.updated_at = timezone.now()
            ticket.save()

            return redirect('ticket:admin_ticket_detail', ticket_id=ticket_id)
    else:
        form = TicketMessageForm()

    # علامت‌گذاری پیام‌ها به عنوان خوانده شده
    ticket.messages.filter(is_admin_reply=False, is_read_admin=False).update(is_read_admin=True)
    ticket.is_read_admin = True
    ticket.save()

    statuses = TicketStatus.objects.all()

    context = {
        'ticket': ticket,
        'form': form,
        'messages': ticket.messages.all().order_by('created_at'),
        'assignments': ticket.assignments.filter(is_active=True),
        'statuses': statuses,
    }
    return render(request, 'ticket_app/admin_ticket_detail.html', context)

@login_required
@superuser_required
def assign_ticket(request, ticket_id):
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, ticket_id=ticket_id)

        # غیرفعال کردن انتساب‌های قبلی
        TicketAssignment.objects.filter(ticket=ticket, is_active=True).update(is_active=False)

        # ایجاد انتساب جدید
        assignment = TicketAssignment.objects.create(
            ticket=ticket,
            admin_user=request.user
        )

        # تغییر وضعیت به "در حال بررسی"
        in_progress_status = TicketStatus.objects.filter(name='در حال بررسی').first()
        if in_progress_status:
            ticket.status = in_progress_status
            ticket.save()

        return JsonResponse({
            'success': True,
            'message': 'تیکت با موفقیت به شما محول شد',
            'admin_name': f'{request.user.name} {request.user.family}'
        })

    return JsonResponse({'success': False, 'message': 'درخواست نامعتبر'})

@login_required
@superuser_required
def change_ticket_status(request, ticket_id):
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
        new_status_id = request.POST.get('status_id')

        try:
            new_status = TicketStatus.objects.get(id=new_status_id)
            ticket.status = new_status
            ticket.save()

            return JsonResponse({
                'success': True,
                'message': f'وضعیت تیکت به "{new_status.name}" تغییر یافت',
                'new_status': new_status.name,
                'new_status_color': new_status.color
            })
        except TicketStatus.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'وضعیت انتخاب شده معتبر نیست'})

    return JsonResponse({'success': False, 'message': 'درخواست نامعتبر'})

@login_required
@superuser_required
def quick_reply(request, ticket_id):
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
        message_text = request.POST.get('message')
        file = request.FILES.get('file')

        if message_text:
            # ایجاد پیام جدید
            message = TicketMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                message=message_text,
                file=file,
                is_admin_reply=True
            )

            # انتساب تیکت اگر انتسابی وجود ندارد
            if not TicketAssignment.objects.filter(ticket=ticket, is_active=True).exists():
                TicketAssignment.objects.create(
                    ticket=ticket,
                    admin_user=request.user
                )

            # بروزرسانی وضعیت تیکت
            ticket.is_read_user = False
            ticket.is_read_admin = True
            ticket.updated_at = timezone.now()

            # تغییر وضعیت به "پاسخ داده شده"
            answered_status = TicketStatus.objects.filter(name='پاسخ داده شده').first()
            if answered_status and not ticket.status.is_closed:
                ticket.status = answered_status

            ticket.save()

            return JsonResponse({
                'success': True,
                'message': 'پاسخ با موفقیت ارسال شد',
                'message_id': message.id
            })
        else:
            return JsonResponse({'success': False, 'message': 'متن پاسخ نمی‌تواند خالی باشد'})

    return JsonResponse({'success': False, 'message': 'درخواست نامعتبر'})

@login_required
@superuser_required
def bulk_action(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        ticket_ids = request.POST.getlist('ticket_ids')

        if not ticket_ids:
            return JsonResponse({'success': False, 'message': 'هیچ تیکتی انتخاب نشده است'})

        if action == 'assign_to_me':
            # انتساب دسته‌ای تیکت‌ها به ادمین فعلی
            for ticket_id in ticket_ids:
                ticket = Ticket.objects.get(id=ticket_id)
                # غیرفعال کردن انتساب‌های قبلی
                TicketAssignment.objects.filter(ticket=ticket, is_active=True).update(is_active=False)
                # ایجاد انتساب جدید
                TicketAssignment.objects.create(
                    ticket=ticket,
                    admin_user=request.user
                )

            return JsonResponse({
                'success': True,
                'message': f'{len(ticket_ids)} تیکت به شما محول شد'
            })

        elif action == 'close_tickets':
            # بستن دسته‌ای تیکت‌ها
            closed_status = TicketStatus.objects.filter(is_closed=True).first()
            if closed_status:
                Ticket.objects.filter(id__in=ticket_ids).update(status=closed_status)
                return JsonResponse({
                    'success': True,
                    'message': f'{len(ticket_ids)} تیکت بسته شد'
                })

        elif action == 'mark_as_read':
            # علامت‌گذاری به عنوان خوانده شده
            Ticket.objects.filter(id__in=ticket_ids).update(is_read_admin=True)
            return JsonResponse({
                'success': True,
                'message': f'{len(ticket_ids)} تیکت به عنوان خوانده شده علامت‌گذاری شد'
            })

    return JsonResponse({'success': False, 'message': 'عملیات نامعتبر'})

@login_required
@superuser_required
def live_stats_api(request):
    stats = {
        'total_tickets': Ticket.objects.count(),
        'open_tickets': Ticket.objects.filter(status__is_closed=False).count(),
        'unread_tickets': Ticket.objects.filter(is_read_admin=False).count(),
        'assigned_to_me': Ticket.objects.filter(
            assignments__admin_user=request.user,
            assignments__is_active=True
        ).count(),
    }
    return JsonResponse(stats)