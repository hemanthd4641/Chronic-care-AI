from django.urls import path
from . import views

urlpatterns = [
    path("medicines/", views.medicine_list, name="medicine_list"),
    path("cart/", views.view_cart, name="view_cart"),
    path("add-to-cart/<int:medicine_id>/", views.add_to_cart, name="add_to_cart"),
    path("remove-from-cart/<int:cart_item_id>/", views.remove_from_cart, name="remove_from_cart"),
]
