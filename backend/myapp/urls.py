from django.urls import path
from . import views

urlpatterns = [
    path('', views.check, name='check'),
    path('api/predict-campus-placements/', views.predict_campus_placements, name='predict-campus-placements'),
    path('api/predict-student-placement/', views.predict_student_placement, name='predict-student-placement'),
    path('api/resume-parser/', views.resume_parser, name='resume-parser'),
    path('api/recommendSkills/', views.recommend_skills, name='recommend-skills')
]
