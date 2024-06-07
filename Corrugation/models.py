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


class Product(models.Model):
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100, unique=True)
    box_no = models.CharField(max_length=8, blank=True)
    material_code = models.CharField(max_length=10, blank=True)
    size = models.CharField(max_length=10, blank=True)  # change this
    inner_length = models.PositiveSmallIntegerField(blank=True)
    inner_breadth = models.PositiveSmallIntegerField(blank=True)
    inner_depth = models.PositiveSmallIntegerField(blank=True)
    outer_length = models.PositiveSmallIntegerField(blank=True)
    outer_breadth = models.PositiveSmallIntegerField(blank=True)
    outer_depth = models.PositiveSmallIntegerField(blank=True)
    color = models.CharField(max_length=20, blank=True)
    weight = models.CharField(max_length=7, blank=True)
    ply = models.CharField(max_length=15, blank=True)
    gsm = models.CharField(max_length=20, blank=True)
    bf = models.CharField(max_length=5, blank=True)
    cs = models.CharField(max_length=5, blank=True)
    archive = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.manager

    def __str__(self):
        return f'{self.product_name}'


class Partition(models.Model):
    product_name = models.ForeignKey(Product, on_delete=models.CASCADE)
    partition_size = models.CharField(max_length=10)  # change this
    partition_od = models.CharField(max_length=50)
    deckle_cut = models.CharField(max_length=1)
    length_cut = models.CharField(max_length=1)
    partition_type_choice = (
        ('vertical', 'Vertical'),
        ('horizontal', 'Horizontal'),
        ('z-type', 'Z-Type'),
        ('crisscross', 'Criss-Cross'),
    )
    partition_type = models.CharField(max_length=10, choices=partition_type_choice)
    ply_no_choices = (
        ('3', '3 Ply'),
        ('5', '5 Ply'),
        ('7', '7 Ply'),
    )
    ply_no = models.CharField(max_length=1, choices=ply_no_choices)
    partition_weight = models.CharField(max_length=7)
    gsm = models.PositiveSmallIntegerField()
    bf = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    object = models.manager

    def __str__(self):
        return f'{self.product_name} - {self.partition_type}'
