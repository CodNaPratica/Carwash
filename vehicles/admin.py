from django.contrib import admin

from .models import VehicleEntry, VehicleEntryLog, VehicleType


@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_approved', 'added_by', 'created_at')
    list_filter = ('is_approved',)
    search_fields = ('name',)


class VehicleEntryLogInline(admin.TabularInline):
    model = VehicleEntryLog
    extra = 0
    readonly_fields = ('changed_by', 'reason', 'snapshot', 'created_at')
    can_delete = False


@admin.register(VehicleEntry)
class VehicleEntryAdmin(admin.ModelAdmin):
    list_display = (
        'plate', 'brand', 'model', 'service', 'status', 'registered_by',
        'is_trashed', 'created_at',
    )
    list_filter = ('status', 'is_trashed', 'service')
    search_fields = ('plate', 'brand', 'model__name')
    inlines = [VehicleEntryLogInline]
