from django.contrib import admin
from .models import (PaperReels, Product, Partition, PurchaseOrder, Dispatch,
                     Program, Production, ProductionReels, Stock)


class PaperReelAdmin(admin.ModelAdmin):
    model = PaperReels
    list_display = ['tenant', 'supplier', 'reel_number']
    list_filter = ['tenant', 'supplier', 'reel_number', 'weight']


admin.site.register(PaperReels, PaperReelAdmin)


class PartitionInline(admin.TabularInline):
    model = Partition
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    inlines = [PartitionInline]
    list_display = ['tenant', 'product_name']
    list_filter = ['tenant__name', 'product_name']


admin.site.register(Product, ProductAdmin)


class DispatchInline(admin.StackedInline):
    model = Dispatch
    extra = 1


class PurchaseOrderAdmin(admin.ModelAdmin):
    inlines = [DispatchInline]
    list_display = ['product_name', 'po_number', 'po_date']
    list_filter = ['product_name', 'po_number', 'po_date']


admin.site.register(PurchaseOrder, PurchaseOrderAdmin)


class ProgramAdmin(admin.ModelAdmin):
    model = Program
    list_display = ['product', 'program_date']
    list_filter = ['product__tenant', 'product__product_name', 'program_date']


admin.site.register(Program, ProgramAdmin)


class ProductionReelInline(admin.StackedInline):
    model = ProductionReels
    extra = 1


class ProductionAdmin(admin.ModelAdmin):
    inlines = [ProductionReelInline]
    model = Production
    list_display = ['product', 'production_date']
    list_filter = ['product__tenant', 'product__product_name', 'production_date']


admin.site.register(Production, ProductionAdmin)


class StockAdmin(admin.ModelAdmin):
    model = Stock
    list_display = ['product', 'tag']
    list_filter = ['product__tenant', 'product', 'tag']


admin.site.register(Stock, StockAdmin)
