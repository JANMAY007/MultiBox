from django.contrib import admin
from .models import Tenant, TenantEmployees, PaperReels


class TenantEmployeesInline(admin.TabularInline):
    model = TenantEmployees
    extra = 1


class TenantAdmin(admin.ModelAdmin):
    inlines = [TenantEmployeesInline]


admin.site.register(Tenant, TenantAdmin)
admin.site.register(PaperReels)
