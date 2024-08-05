from django.contrib import admin
from .models import Challan, ChallanItem


class ChallanItemInline(admin.StackedInline):
    model = ChallanItem
    extra = 1


class ChallanAdmin(admin.ModelAdmin):
    inlines = [ChallanItemInline]
    list_display = ['tenant', 'challan_no', 'order_no']
    list_filter = ['tenant', 'challan_date', 'order_date']


admin.site.register(Challan, ChallanAdmin)
