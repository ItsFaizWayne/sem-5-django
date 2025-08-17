# rentals/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('request/<int:game_id>/', views.request_rental, name='request_rental'),
    path('my-rentals/', views.my_rentals, name='my_rentals'),
    path('update-status/<int:rental_id>/<str:new_status>/', views.update_rental_status, name='update_rental_status'),
    path('update-status/<int:rental_id>/<str:new_status>/', views.update_rental_status, name='update_rental_status'),
    # path('approve/<int:rental_id>/', views.approve_rental, name='approve_rental'),
    # path('reject/<int:rental_id>/', views.reject_rental, name='reject_rental'),
]
