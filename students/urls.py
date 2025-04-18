from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('profile/', views.student_profile, name='student_profile'),
    
     path('change-password/', views.student_change_password, name='change_password'),
    path('application/withdraw/<int:application_id>/', views.withdraw_application, name='withdraw_application'),
    path('college/applications/', views.college_applications, name='college_applications'),
    path('school/applications/', views.school_applications, name='school_applications'),
    path('application/<int:application_id>/', views.view_school_application, name='view_school_application'),
    path('college-application/<int:application_id>/', views.view_application_details, name='view_college_application_details'),
    path('application/<int:application_id>/download/', views.download_college_application, name='download_college_application'),
]