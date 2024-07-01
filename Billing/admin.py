from django.contrib import admin
from .models import Challan, ChallanItem


class ChallanItemInline(admin.StackedInline):
    model = ChallanItem
    extra = 0


class ChallanAdmin(admin.ModelAdmin):
    inlines = [ChallanItemInline]


admin.site.register(Challan, ChallanAdmin)
