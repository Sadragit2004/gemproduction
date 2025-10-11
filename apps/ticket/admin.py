# admin.py
from django.contrib import admin
from .models import (
    TicketDepartment, TicketPriority, TicketStatus,
    Ticket, TicketMessage, TicketAssignment
)

@admin.register(TicketDepartment)
class TicketDepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']

@admin.register(TicketPriority)
class TicketPriorityAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'order']
    list_editable = ['color', 'order']
    ordering = ['order']

@admin.register(TicketStatus)
class TicketStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'is_closed']
    list_filter = ['is_closed']
    list_editable = ['color', 'is_closed']

class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 0
    readonly_fields = ['created_at']
    fields = ['sender', 'message', 'file', 'is_admin_reply', 'created_at']

class TicketAssignmentInline(admin.TabularInline):
    model = TicketAssignment
    extra = 0
    readonly_fields = ['assigned_at']
    fields = ['admin_user', 'assigned_at', 'is_active']

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        'ticket_id', 'user', 'subject', 'department', 'priority',
        'status', 'is_read_admin', 'is_read_user', 'created_at'
    ]
    list_filter = [
        'department', 'priority', 'status', 'is_read_admin',
        'is_read_user', 'created_at'
    ]
    search_fields = [
        'ticket_id', 'user__mobileNumber', 'user__name',
        'user__family', 'subject'
    ]
    readonly_fields = ['ticket_id', 'created_at', 'updated_at']
    inlines = [TicketMessageInline, TicketAssignmentInline]
    list_per_page = 50

@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'sender', 'is_admin_reply', 'created_at']
    list_filter = ['is_admin_reply', 'created_at']
    search_fields = ['ticket__ticket_id', 'sender__mobileNumber', 'message']
    readonly_fields = ['created_at']

@admin.register(TicketAssignment)
class TicketAssignmentAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'admin_user', 'assigned_at', 'is_active']
    list_filter = ['is_active', 'assigned_at']
    search_fields = ['ticket__ticket_id', 'admin_user__mobileNumber']
    readonly_fields = ['assigned_at']