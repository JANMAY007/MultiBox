from django.urls import path
from .views import challans, add_challan

app_name = 'Billing'

urlpatterns = [
    path('challans/', challans, name='challans'),
    path('add_challan/', add_challan, name='add_challan'),
]
