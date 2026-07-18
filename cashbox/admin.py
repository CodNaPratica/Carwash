from django.contrib import admin

from .models import CashClosure, CashMovement, Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('vehicle_entry', 'service', 'amount', 'received_by', 'created_at')
    list_filter = ('service',)
    date_hierarchy = 'created_at'


@admin.register(CashMovement)
class CashMovementAdmin(admin.ModelAdmin):
    list_display = ('category', 'amount', 'registered_by', 'created_at')
    list_filter = ('category',)
    date_hierarchy = 'created_at'


@admin.register(CashClosure)
class CashClosureAdmin(admin.ModelAdmin):
    list_display = (
        'period_type', 'date_start', 'date_end', 'total_in', 'total_out',
        'balance', 'carried_forward', 'closed_by', 'closed_at',
    )
    list_filter = ('period_type',)
