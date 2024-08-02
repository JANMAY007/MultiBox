from django.db import models
from Tenant.models import Tenant


class PlanPurchase(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    PAYMENT_CHOICES = (
        ('SUCCESS', 'SUCCESS'),
        ('FAILURE', 'FAILURE'),
        ('PENDING', 'PENDING')
    )
    status = models.CharField(max_length=254, choices=PAYMENT_CHOICES, default="PENDING", blank=False, null=False)
    order_name = models.CharField(max_length=254, blank=False, null=False)
    order_amount = models.FloatField(null=False, blank=False)
    provider_order_id = models.CharField(max_length=40, null=True, blank=True)
    payment_id = models.CharField(max_length=36, null=False, blank=False)
    signature_id = models.CharField(max_length=128, null=False, blank=False)
    objects = models.manager
