from django.contrib import admin
from .models import Tenant, TenantEmployees, PaperReels, Product, Partition


admin.site.register(PaperReels)


class TenantEmployeesInline(admin.TabularInline):
    model = TenantEmployees
    extra = 1


class TenantAdmin(admin.ModelAdmin):
    inlines = [TenantEmployeesInline]


admin.site.register(Tenant, TenantAdmin)


class PartitionInline(admin.TabularInline):
    model = Partition
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    inlines = [PartitionInline]


admin.site.register(Product, ProductAdmin)
