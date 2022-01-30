from django.urls import path
from .views import BitcoinView

urlpatterns=[
    path('', BitcoinView, name='bitcoin'),
]
