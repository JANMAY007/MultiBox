from django.urls import path
from .views import (search_reels, paper_reels, update_reel, delete_reel,
                    restore_reel, add_product, product_archive, update_products,
                    delete_products, restore_products, products_detail,
                    product_detail_archive, register_tenant, purchase_order,
                    add_purchase_order_detail, add_purchase_order_detailed,
                    purchase_order_archive, purchase_order_detail_archive,
                    delete_purchase_order, add_dispatch)

app_name = 'Corrugation'

urlpatterns = [
    path('register_tenant/', register_tenant, name='register_tenant'),
    path('paper_reels/', paper_reels, name='paper_reels'),
    path('search_reels/', search_reels, name='search_reels'),
    path('update_reel/<int:pk>/', update_reel, name='update_reel'),
    path('delete_reel/<int:pk>/', delete_reel, name='delete_reel'),
    path('restore_reel/<int:pk>/', restore_reel, name='restore_reel'),
    path('add_product/', add_product, name='add_product'),
    path('product_archive/', product_archive, name='product_archive'),
    path('update_products/<int:pk>/', update_products, name='update_products'),
    path('delete_products/<int:pk>/', delete_products, name='delete_products'),
    path('restore_products/<int:pk>/', restore_products, name='restore_products'),
    path('products_detail/<int:pk>/', products_detail, name='products_detail'),
    path('product_detail_archive/<int:pk>/', product_detail_archive, name='product_detail_archive'),
    path('purchase_order/', purchase_order, name='purchase_order'),
    path('add_purchase_order_detail/', add_purchase_order_detail, name='add_purchase_order_detail'),
    path('add_purchase_order_detailed/', add_purchase_order_detailed, name='add_purchase_order_detailed'),
    path('purchase_order_archive/', purchase_order_archive, name='purchase_order_archive'),
    path('purchase_order_detail_archive/<int:pk>/', purchase_order_detail_archive, name='purchase_order_detail_archive'),
    path('delete_purchase_order/<int:pk>/', delete_purchase_order, name='delete_purchase_order'),
    path('add_dispatch/', add_dispatch, name='add_dispatch'),
]
