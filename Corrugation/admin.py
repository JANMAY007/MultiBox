from django.contrib import admin
from .models import (Tenant, TenantEmployees, PaperReels, Product, Partition,
                     PurchaseOrder, Dispatch, Program, Production, ProductionReels,
                     Stock, TenantGeneralInfo, TenantPaymentInfo, TenantAddress, TenantBuyers)


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


class DispatchInline(admin.StackedInline):
    model = Dispatch
    extra = 1


class PurchaseOrderAdmin(admin.ModelAdmin):
    inlines = [DispatchInline]


admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
admin.site.register(Program)
admin.site.register(Production)
admin.site.register(ProductionReels)
admin.site.register(Stock)
admin.site.register(TenantGeneralInfo)
admin.site.register(TenantPaymentInfo)
admin.site.register(TenantAddress)
admin.site.register(TenantBuyers)
