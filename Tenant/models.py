from django.db import models
from django.contrib.auth.models import User


def tenant_logo_path(instance, filename):
    return f'tenant_logo/{instance.name}/{filename}'


class Tenant(models.Model):
    class Meta:
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'

    name = models.CharField(max_length=100, unique=True, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    tenant_gst_number = models.CharField(max_length=15, null=True, blank=True)
    active = models.BooleanField(default=True)
    tenant_logo = models.ImageField(upload_to=tenant_logo_path)
    amount_decided = models.FloatField(null=True, blank=True)
    email = models.EmailField()
    email_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=15)
    phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    object = models.manager

    def __str__(self):
        return f'{self.name} - {self.amount_decided}'


class TenantAddress(models.Model):
    class Meta:
        verbose_name = 'Tenant Address'
        verbose_name_plural = 'Tenant Addresses'

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    plot_no = models.CharField(max_length=20)
    address_line_1 = models.CharField(max_length=150)
    address_line_2 = models.CharField(max_length=150)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=6)
    country = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    object = models.manager

    def __str__(self):
        return f'{self.tenant.name} - {self.city}'


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


class TenantGeneralInfo(models.Model):
    class Meta:
        verbose_name = 'Tenant General Info'
        verbose_name_plural = 'Tenant General Infos'

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    total_storage = models.PositiveIntegerField(default=50)
    reels_delete_before_days = models.PositiveSmallIntegerField(default=15)
    program_delete_before_days = models.PositiveSmallIntegerField(default=5)
    production_delete_before_days = models.PositiveSmallIntegerField(default=5)
    purchase_order_delete_before_days = models.PositiveSmallIntegerField(default=15)
    database_copy = models.BooleanField(default=False)
    monthly_report = models.BooleanField(default=False)
    premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    object = models.manager

    def __str__(self):
        return f'{self.tenant}'


class TenantBuyers(models.Model):
    class Meta:
        verbose_name = 'Tenant Buyer'
        verbose_name_plural = 'Tenant Buyers'
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    buyer_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    object = models.manager

    def __str__(self):
        return f'{self.tenant} - {self.buyer_name}'
