from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListCreateOrderView.as_view(), name="new_order"),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail')
]