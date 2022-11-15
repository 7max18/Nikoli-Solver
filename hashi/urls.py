from django.urls import path

from . import views

urlpatterns = [
    path('', views.HashiFormView.as_view(), name='index'),
]