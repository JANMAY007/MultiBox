from django.contrib import admin
from .models import (Tenant, TenantEmployees, TenantGeneralInfo,
                     TenantAddress, TenantBuyers)


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
    inlines = [TenantAddressInline, TenantGeneralInfo, TenantEmployeesInline, TenantBuyersInline]


admin.site.register(Tenant, TenantAdmin)
