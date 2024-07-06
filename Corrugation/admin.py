from django.contrib import admin
from .models import (PaperReels, Product, Partition, PurchaseOrder, Dispatch,
                     Program, Production, ProductionReels, Stock)


admin.site.register(PaperReels)


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
