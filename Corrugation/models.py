from django.db import models
from django.contrib.auth.models import User
from Tenant.models import Tenant


class PaperReels(models.Model):
    class Meta:
        verbose_name = 'Paper Reel'
        verbose_name_plural = 'Paper Reels'

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    supplier = models.CharField(max_length=50)
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
        constraints = [
            models.UniqueConstraint(fields=['tenant', 'product_name'], name='unique_tenant_product_name')
        ]

    product_name = models.CharField(max_length=100)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    box_no = models.CharField(max_length=8, null=True, blank=True)
    material_code = models.CharField(max_length=10, null=True, blank=True)
    size = models.CharField(max_length=10, null=True, blank=True)
    inner_length = models.PositiveSmallIntegerField(null=True, blank=True)
    inner_breadth = models.PositiveSmallIntegerField(null=True, blank=True)
    inner_depth = models.PositiveSmallIntegerField(null=True, blank=True)
    outer_length = models.PositiveSmallIntegerField(null=True, blank=True)
    outer_breadth = models.PositiveSmallIntegerField(null=True, blank=True)
    outer_depth = models.PositiveSmallIntegerField(null=True, blank=True)
    color = models.CharField(max_length=20, null=True, blank=True)
    weight = models.CharField(max_length=7, null=True, blank=True)
    ply = models.CharField(max_length=15, null=True, blank=True)
    gsm = models.CharField(max_length=20, null=True, blank=True)
    bf = models.CharField(max_length=5, null=True, blank=True)
    cs = models.CharField(max_length=5, null=True, blank=True)
    archive = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.manager

    def __str__(self):
        return f'{self.product_name} - {self.tenant.name}'


class Partition(models.Model):
    product_name = models.ForeignKey(Product, on_delete=models.CASCADE)
    partition_size = models.CharField(max_length=10)
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


class PurchaseOrder(models.Model):
    class Meta:
        verbose_name = 'Purchase Order'
        verbose_name_plural = 'Purchase Orders'

    product_name = models.ForeignKey(Product, on_delete=models.CASCADE)
    po_given_by = models.CharField(max_length=100)
    po_number = models.CharField(max_length=10)
    po_date = models.DateField()
    rate = models.FloatField()
    po_quantity = models.PositiveIntegerField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.manager

    def __str__(self):
        return f'{self.product_name} - {self.po_date} - {self.po_number}'


class Dispatch(models.Model):
    class Meta:
        verbose_name = 'Dispatch'
        verbose_name_plural = 'Dispatches'

    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    dispatch_date = models.DateField()
    dispatch_quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.manager

    def __str__(self):
        return f'{self.po} - {self.dispatch_date}'


class Program(models.Model):
    class Meta:
        verbose_name = 'Program'
        verbose_name_plural = 'Programs'
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    program_quantity = models.PositiveIntegerField()
    program_date = models.DateField()
    program_notes = models.TextField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.manager

    def __str__(self):
        return f'{self.program_date}'


class Production(models.Model):
    class Meta:
        verbose_name = 'Production'
        verbose_name_plural = 'Productions'
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    production_date = models.DateField()
    production_quantity = models.PositiveIntegerField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.manager

    def __str__(self):
        return f'{self.product} - {self.production_date}'


class ProductionReels(models.Model):
    class Meta:
        verbose_name = 'Production Reel'
        verbose_name_plural = 'Production Reels'
    production = models.ForeignKey(Production, on_delete=models.CASCADE)
    reel = models.ForeignKey(PaperReels, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.manager

    def __str__(self):
        return f'{self.production} - {self.reel}'


class Stock(models.Model):
    class Meta:
        verbose_name = 'Stock'
        verbose_name_plural = 'Stocks'
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.manager

    def __str__(self):
        return f'{self.product} - {self.stock_quantity}'
