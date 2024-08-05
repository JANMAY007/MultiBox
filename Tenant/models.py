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
    email = models.EmailField()
    email_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=15)
    phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    object = models.manager


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


class TenantEmployees(models.Model):
    class Meta:
        verbose_name = 'Tenant Employee'
        verbose_name_plural = 'Tenant Employees'

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    object = models.manager


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


class TenantBuyers(models.Model):
    class Meta:
        verbose_name = 'Tenant Buyer'
        verbose_name_plural = 'Tenant Buyers'
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    buyer_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    object = models.manager


class TenantPlan(models.Model):
    class Meta:
        verbose_name = 'Tenant Plan'
        verbose_name_plural = 'Tenant Plans'
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    PLAN_CHOICES = [
        ('m_s', 'Standard Monthly'),
        ('m_e', 'Enterprise Monthly'),
        ('y_s', 'Standard Yearly'),
        ('y_e', 'Enterprise Yearly'),
    ]
    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    # True with history and false without history
    stock_management_and_history = models.BooleanField(default=False)
    # True with smart addition and false without smart addition
    smart_bulk_reel_addition = models.BooleanField(default=False)
    # True with advance filters and false with basic filters
    reel_filtering = models.BooleanField(default=False)
    reels_stocks_and_order_management = models.BooleanField(default=False)
    products_management = models.BooleanField(default=False)
    products_filtering = models.BooleanField(default=False)
    production_line_handling = models.BooleanField(default=False)
    daily_program_management = models.BooleanField(default=False)
    daily_program_sharing = models.BooleanField(default=False)
    purchase_order_management = models.BooleanField(default=False)
    monthly_report = models.BooleanField(default=False)
    database_copy = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    active_till = models.DateTimeField()
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
