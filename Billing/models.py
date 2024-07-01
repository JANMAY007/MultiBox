from django.db import models
from Corrugation.models import Tenant, PurchaseOrder


class Challan(models.Model):
    class Meta:
        verbose_name = 'Challan'
        verbose_name_plural = 'Challans'

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    order_no = models.CharField(max_length=20)
    order_date = models.DateField()
    challan_no = models.CharField(max_length=20)
    challan_date = models.DateField()
    billing_to = models.TextField()
    shipping_to = models.TextField()
    vehicle_no = models.CharField(max_length=15)
    challan_note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    object = models.manager

    def __str__(self):
        return f'{self.tenant.name} - {self.challan_no}'


class ChallanItem(models.Model):
    class Meta:
        verbose_name = 'Challan Item'
        verbose_name_plural = 'Challan Items'

    challan = models.ForeignKey(Challan, on_delete=models.CASCADE)
    challan_po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    bundles = models.JSONField(default=dict)
    quantity = models.IntegerField()
    remarks = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    object = models.manager

    def __str__(self):
        return f'{self.challan.challan_no}'
