from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("transactions/new/", views.transaction_create, name="transaction_create"),
    path(
        "transactions/<int:transaction_id>/delete/",
        views.transaction_delete,
        name="transaction_delete",
    ),
    path("categories/", views.category_list, name="categories"),
    path(
        "categories/<int:category_id>/delete/",
        views.category_delete,
        name="category_delete",
    ),
]
