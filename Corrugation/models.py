from django.db import models
from django.contrib.auth.models import User


class Tenant(models.Model):
    class Meta:
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    tenant_logo = models.ImageField(upload_to='tenant_logo/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    object = models.manager

    def __str__(self):
        return f'{self.name}'


class TenantEmployees(models.Model):
    class Meta:
        verbose_name = 'Tenant Employee'
        verbose_name_plural = 'Tenant Employees'
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    object = models.manager

    def __str__(self):
        return f'{self.user.username}'


class PaperReels(models.Model):
    class Meta:
        verbose_name = 'Paper Reel'
        verbose_name_plural = 'Paper Reels'
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    reel_number = models.CharField(max_length=15)
    bf = models.PositiveSmallIntegerField(default=18)
    gsm = models.PositiveSmallIntegerField(default=120)
    size = models.FloatField(default=41)
    weight = models.PositiveSmallIntegerField(default=545)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    object = models.manager

    def __str__(self):
        return f'{self.reel_number}'
