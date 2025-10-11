# apps/ticket/urls.py
from django.urls import path
from . import views

app_name = 'ticket'

urlpatterns = [
    # کاربر عادی
    path('', views.ticket_list, name='ticket_list'),
    path('create/', views.create_ticket, name='create_ticket'),
    path('<str:ticket_id>/', views.ticket_detail, name='ticket_detail'),

    # ادمین
    path('t/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/<str:ticket_id>/', views.admin_ticket_detail, name='admin_ticket_detail'),
    path('admin/<str:ticket_id>/assign/', views.assign_ticket, name='assign_ticket'),
    path('admin/<str:ticket_id>/change-status/', views.change_ticket_status, name='change_ticket_status'),
    path('admin/<str:ticket_id>/quick-reply/', views.quick_reply, name='quick_reply'),
    path('admin/bulk-action/', views.bulk_action, name='bulk_action'),
    path('admin/stats/api/', views.live_stats_api, name='live_stats_api'),
]