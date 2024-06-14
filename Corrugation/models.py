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
    amount_decided = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    object = models.manager

    def __str__(self):
        return f'{self.name} - {self.amount_decided}'


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
    total_storage = models.PositiveIntegerField()
    delete_before_days = models.PositiveSmallIntegerField()
    database_copy = models.BooleanField(default=False)
    monthly_report = models.BooleanField(default=False)
    premium = models.BooleanField(default=False)
    object = models.manager

    def __str__(self):
        return f'{self.tenant}'


class TenantPaymentInfo(models.Model):
    class Meta:
        verbose_name = 'Tenant Payment Info'
        verbose_name_plural = 'Tenant Payment Infos'

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    payment_datetime = models.DateTimeField()
    object = models.manager

    def __str__(self):
        return f'{self.tenant.name} - {self.payment_datetime}'


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
        constraints = [
            models.UniqueConstraint(fields=['tenant', 'product_name'], name='unique_tenant_product_name')
        ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)
    box_no = models.CharField(max_length=8, blank=True)
    material_code = models.CharField(max_length=10, blank=True)
    size = models.CharField(max_length=10, blank=True)
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
    po_given_by = models.CharField(max_length=50)
    po_number = models.CharField(max_length=10)
    po_date = models.DateField()
    rate = models.FloatField()
    po_quantity = models.PositiveIntegerField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.manager

    def save(self, *args, **kwargs):
        self._meta.get_field('po_given_by').choices = self.get_po_given_by_choices()
        super().save(*args, **kwargs)

    def get_po_given_by_choices(self):
        tenant = getattr(self, 'tenant', None)
        if tenant:
            if tenant.name == 'Shiv Packaging':
                return [
                    ('Sweety Industries', 'Sweety Industries'),
                    ('Sweetco Foods', 'Sweetco Foods'),
                    ('VR Agro Processors LLP', 'VR Agro Processors LLP'),
                    ('Lao More Biscuits Pvt Ltd', 'Lao More Biscuits Pvt Ltd'),
                    ('Makson Pharmaceuticals I Pvt Ltd', 'Makson Pharmaceuticals I Pvt Ltd'),
                    ('GP Manglani Foods Pvt Ltd', 'GP Manglani Foods Pvt Ltd'),
                    ('KMM Foods Pvt Ltd', 'KMM Foods Pvt Ltd'),
                    ('Parle Product Pvt Ltd', 'Parle Product Pvt Ltd'),
                    ('JRJ Foods Pvt Ltd', 'JRJ Foods Pvt Ltd'),
                    ('RZ Dholakia', 'RZ Dholakia'),
                    ('Ishwar Snuff Works', 'Ishwar Snuff Works'),
                    ('Parag Perfumes', 'Parag Perfumes'),
                ]
            else:
                return []
        return []

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
