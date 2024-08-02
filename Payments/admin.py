from django.contrib import admin
from .models import PlanPurchase


@admin.register(PlanPurchase)
class ProductPurchaseAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'status', 'order_name', 'order_amount')
