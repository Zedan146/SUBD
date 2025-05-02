from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/assign/', views.assign_courier, name='assign_courier'),
    path('order/new/', views.OrderCreateView.as_view(), name='order_create'),
    path('order/<int:pk>/edit/', views.OrderUpdateView.as_view(), name='order_edit'),
    path('order/<int:order_id>/status/', views.change_status, name='change_status'),
    path('order/<int:order_id>/cancel/', views.cancel_order, name='order_cancel'),
]
