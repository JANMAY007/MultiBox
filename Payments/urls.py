from django.urls import path
from .views import plan_purchase_payment, plan_purchase_callback


app_name = 'Payments'

urlpatterns = [
    path('plan_purchase_payment/<int:plan_id>/', plan_purchase_payment, name="plan_purchase_payment"),
    path('plan_purchase_callback/', plan_purchase_callback, name="plan_purchase_callback")
]
