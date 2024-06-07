from django.urls import path
from .views import (search_reels, paper_reels, update_reel, delete_reel,
                    restore_reel, add_product, product_archive, update_products,
                    delete_products, restore_products, products_detail,
                    product_detail_archive, register_tenant)

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
]
