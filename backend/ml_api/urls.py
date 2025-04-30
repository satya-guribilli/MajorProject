from django.urls import path
from . import views

urlpatterns = [
    path('predict/salary/', views.predict_salary, name='predict_salary'),
    path('predict/placement/', views.predict_placement, name='predict_placement'),
]
