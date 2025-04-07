from django.urls import path
from . import views
urlpatterns = [
    path('',views.table, name='table' ),
    path('hv/menu', views.menu, name='menu'),
    path('hv/menu/booking/', views.book_table, name='tables'),
    path('hv/menu/booking/confirmation/', views.confirm, name='confirmation'),
    path('hv/menu/booking/contact', views.contact, name='contact'),
    path('delete-past-bookings/', views.delete_past_bookings_view, name='delete_past_bookings'),
    path('error/', views.error_view, name='error'),
]