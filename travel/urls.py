from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_view, name='my-view'),
    path('test', views.test, name='test'),
    path('autocomplete',views.amadeus_location_autocomplete,name="autocomplete"),
    path('book', views.book_flight, name='book_flight')


]
