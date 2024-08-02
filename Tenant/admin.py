from django.contrib import admin
from .models import (Tenant, TenantEmployees, TenantGeneralInfo,
                     TenantAddress, TenantBuyers, TenantPlan)


class TenantAddressInline(admin.StackedInline):
    model = TenantAddress
    extra = 0


class TenantGeneralInfoInline(admin.StackedInline):
    model = TenantGeneralInfo
    extra = 0


class TenantEmployeesInline(admin.StackedInline):
    model = TenantEmployees
    extra = 1


class TenantBuyersInline(admin.StackedInline):
    model = TenantBuyers
    extra = 1


class TenantAdmin(admin.ModelAdmin):
    inlines = [TenantAddressInline, TenantGeneralInfoInline, TenantEmployeesInline, TenantBuyersInline]
    list_display = ['name', 'owner', 'tenant_gst_number', 'active', 'email', 'phone']


admin.site.register(Tenant, TenantAdmin)


class TenantPlanAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'active_till', 'active']


admin.site.register(TenantPlan, TenantPlanAdmin)
