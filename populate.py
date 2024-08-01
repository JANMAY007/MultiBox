import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MultiBox.settings')
django.setup()

from Corrugation.models import (PaperReels, Product, Production, ProductionReels,
                                Stock, Partition, PurchaseOrder, Dispatch)
from Tenant.models import Tenant


def random_date(start, end):
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds())),
    )


tenant = Tenant.objects.first()


def create_paper_reels(n=10):
    for _ in range(n):
        PaperReels.objects.create(
            tenant=tenant,
            supplier=f'Supplier_{random.randint(1, 100)}',
            reel_number=f'R_{random.randint(1000, 9999)}',
            bf=random.randint(18, 22),
            gsm=random.randint(100, 150),
            size=random.uniform(40.0, 50.0),
            weight=random.randint(500, 600),
            used=random.choice([True, False]),
        )


def create_products(n=10):
    existing_product_names = set(Product.objects.filter(tenant=tenant).values_list('product_name', flat=True))
    for _ in range(n):
        product_name = f'Product_{random.randint(1, 1000)}'
        while product_name in existing_product_names:
            product_name = f'Product_{random.randint(1, 1000)}'
        existing_product_names.add(product_name)
        Product.objects.create(
            tenant=tenant,
            product_name=product_name,
            box_no=f'B_{random.randint(100, 999)}',
            material_code=f'MC_{random.randint(1000, 9999)}',
            size=f'S_{random.randint(1, 10)}',
            inner_length=random.randint(10, 50),
            inner_breadth=random.randint(10, 50),
            inner_depth=random.randint(10, 50),
            outer_length=random.randint(50, 100),
            outer_breadth=random.randint(50, 100),
            outer_depth=random.randint(50, 100),
            color=f'Color_{random.randint(1, 10)}',
            weight=f'{random.uniform(1.0, 10.0):.2f} kg',
        )


def random_partition_data(product):
    partition_sizes = ['10x10', '20x20', '30x30']
    partition_od_values = ['OD1', 'OD2', 'OD3']
    deckle_cuts = [1, 2, 3]
    length_cuts = [1, 2, 3]
    partition_types = ['vertical', 'horizontal', 'z-type', 'crisscross']
    ply_numbers = ['3', '5', '7']
    partition_weights = ['1.0 kg', '1.5 kg', '2.0 kg']
    gsm_values = [100, 150, 200]
    bf_values = [18, 22, 25]

    return Partition(
        product_name=product,
        partition_size=random.choice(partition_sizes),
        partition_od=random.choice(partition_od_values),
        deckle_cut=random.choice(deckle_cuts),
        length_cut=random.choice(length_cuts),
        partition_type=random.choice(partition_types),
        ply_no=random.choice(ply_numbers),
        partition_weight=random.choice(partition_weights),
        gsm=random.choice(gsm_values),
        bf=random.choice(bf_values)
    )


def add_partitions_to_products():
    products = Product.objects.all()
    for product in products:
        num_partitions = random.randint(0, 2)
        for _ in range(num_partitions):
            partition = random_partition_data(product)
            partition.save()


def create_productions(n=10):
    products = list(Product.objects.all())
    for _ in range(n):
        product = random.choice(products)
        Production.objects.create(
            product=product,
            production_date=random_date(datetime(2020, 1, 1), datetime(2023, 12, 31)),
            production_quantity=random.randint(100, 1000),
            active=random.choice([True, False]),
        )


def create_production_reels(n=10):
    productions = list(Production.objects.all())
    reels = list(PaperReels.objects.all())
    for _ in range(n):
        production = random.choice(productions)
        reel = random.choice(reels)
        ProductionReels.objects.create(
            production=production,
            reel=reel,
        )


def create_stock(n=10):
    products = list(Product.objects.all())
    tags = ['liners', 'top', 'sheets', 'box', 'partition']
    for _ in range(n):
        product = random.choice(products)
        Stock.objects.create(
            product=product,
            stock_quantity=random.randint(0, 1000),
            tag=random.choice(tags),
        )


def random_po_data(product, num_pos):
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2023, 12, 31)
    po_dates = [start_date + timedelta(days=random.randint(0, (end_date - start_date).days)) for _ in range(num_pos)]
    po_dates.sort()

    for po_date in po_dates:
        PurchaseOrder.objects.create(
            product_name=product,
            po_given_by=f'Buyer_{random.randint(1, 100)}',
            po_number=f'PO_{random.randint(1000, 9999)}',
            po_date=po_date,
            rate=random.uniform(10.0, 100.0),
            po_quantity=random.randint(100, 1000),
            active=random.choice([True, False])
        )


def add_purchase_orders_to_products():
    products = Product.objects.all()
    for product in products:
        num_pos = random.randint(1, 8)
        for _ in range(num_pos):
            random_po_data(product, num_pos)


if __name__ == '__main__':
    create_paper_reels(100)
    create_products(100)
    add_partitions_to_products()
    create_productions(100)
    create_production_reels(100)
    create_stock(100)
    add_purchase_orders_to_products()
    print("Sample data created successfully.")
