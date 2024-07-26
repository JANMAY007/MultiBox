from django.urls import path
from .views import (search_reels, paper_reels, update_reel, delete_reel, reels_stock,
                    restore_reel, add_product, product_archive, update_products,
                    add_partition, update_partition, delete_partition,
                    delete_products, restore_products, products_detail,
                    product_detail_archive, purchase_order, summary,
                    add_purchase_order_detail, add_purchase_order_detailed,
                    purchase_order_archive, purchase_order_detail_archive,
                    delete_purchase_order, restore_purchase_order, add_dispatch, daily_program,
                    program_archive, edit_program_view, delete_program_view, production,
                    production_archive, update_production_quantity, add_reel_to_production,
                    delete_production, stocks, delete_stock,
                    contact_support, upload_bulk_reels, offline)

app_name = 'Corrugation'

urlpatterns = [
    path('offline/', offline, name='offline'),
    path('contact_support/', contact_support, name='contact_support'),
    path('paper_reels/', paper_reels, name='paper_reels'),
    path('upload_bulk_reels/', upload_bulk_reels, name='upload_bulk_reels'),
    path('search_reels/', search_reels, name='search_reels'),
    path('summary/', summary, name='summary'),
    path('update_reel/<int:pk>/', update_reel, name='update_reel'),
    path('delete_reel/<int:pk>/', delete_reel, name='delete_reel'),
    path('restore_reel/<int:pk>/', restore_reel, name='restore_reel'),
    path('reels_stock/', reels_stock, name='reels_stock'),
    path('', stocks, name='stocks'),
    path('delete_stocks/<int:pk>/', delete_stock, name='delete_stock'),
    path('add_product/', add_product, name='add_product'),
    path('product_archive/', product_archive, name='product_archive'),
    path('update_products/<int:pk>/', update_products, name='update_products'),
    path('delete_products/<int:pk>/', delete_products, name='delete_products'),
    path('restore_products/<int:pk>/', restore_products, name='restore_products'),
    path('add_partition/', add_partition, name='add_partition'),
    path('update_partition/<int:pk>/', update_partition, name='update_partition'),
    path('delete_partition/<int:pk>/', delete_partition, name='delete_partition'),
    path('products_detail/<int:pk>/', products_detail, name='products_detail'),
    path('product_detail_archive/<int:pk>/', product_detail_archive, name='product_detail_archive'),
    path('purchase_order/', purchase_order, name='purchase_order'),
    path('add_purchase_order_detail/<str:po_given_by>/', add_purchase_order_detail, name='add_purchase_order_detail'),
    path('add_purchase_order_detailed/', add_purchase_order_detailed, name='add_purchase_order_detailed'),
    path('purchase_order_archive/', purchase_order_archive, name='purchase_order_archive'),
    path('purchase_order_detail_archive/<str:po_given_by>/', purchase_order_detail_archive, name='purchase_order_detail_archive'),
    path('delete_purchase_order/<int:pk>/', delete_purchase_order, name='delete_purchase_order'),
    path('restore-purchase-order/<int:pk>/', restore_purchase_order, name='restore_purchase_order'),
    path('add_dispatch/', add_dispatch, name='add_dispatch'),
    path('daily_program/', daily_program, name='daily_program'),
    path('program_archive/', program_archive, name='program_archive'),
    path('edit_program_view/', edit_program_view, name='edit_program_view'),
    path('delete_program_view/', delete_program_view, name='delete_program_view'),
    path('production/', production, name='production'),
    path('production_archive/', production_archive, name='production_archive'),
    path('update_production_quantity/', update_production_quantity, name='update_production_quantity'),
    path('add_reel_to_production/', add_reel_to_production, name='add_reel_to_production'),
    path('delete_production/', delete_production, name='delete_production'),
]
