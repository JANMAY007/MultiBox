from django.contrib import admin
from .models import (Tenant, TenantEmployees, TenantGeneralInfo,
                     TenantPaymentInfo, TenantAddress, TenantBuyers)


class TenantEmployeesInline(admin.TabularInline):
    model = TenantEmployees
    extra = 1


class TenantAdmin(admin.ModelAdmin):
    inlines = [TenantEmployeesInline]


admin.site.register(Tenant, TenantAdmin)
admin.site.register(TenantGeneralInfo)
admin.site.register(TenantPaymentInfo)
admin.site.register(TenantAddress)
admin.site.register(TenantBuyers)
