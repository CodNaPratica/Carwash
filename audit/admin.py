from django.contrib import admin

from .models import Reconciliation


@admin.register(Reconciliation)
class ReconciliationAdmin(admin.ModelAdmin):
    list_display = ('date', 'status', 'investigation_status', 'vehicle_entry', 'payment', 'reviewed_by')
    list_filter = ('status', 'investigation_status', 'date')
