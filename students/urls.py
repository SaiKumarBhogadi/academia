from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('profile/', views.student_profile, name='student_profile'),
    path('application/withdraw/<int:application_id>/', views.withdraw_application, name='withdraw_application'),
     path('change-password/', views.student_change_password, name='change_password'),
]