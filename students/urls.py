from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('profile/', views.student_profile, name='student_profile'),
    path('student-register/', views.student_register, name='student_register'),
    path('profile/edit/', views.edit_student_profile, name='edit_student_profile'),
        path('update-details/', views.update_student_details, name='update_student_details'),
        path('details-updated/', views.student_details_updated, name='student_details_updated'),
   
     path('change-password/', views.student_change_password, name='change_password'),
    path('application/withdraw/<int:application_id>/', views.withdraw_application, name='withdraw_application'),
   path('applications/', views.my_applications, name='my_applications'),

   
    path('application/<int:application_id>/', views.view_school_application, name='view_school_application'),
    path('school-application/<int:application_id>/download/', views.download_school_application, name='download_school_application'),
    path('college-application/<int:application_id>/', views.view_application_details, name='view_college_application_details'),
    path('college-application/<int:application_id>/download/', views.download_college_application, name='download_college_application'),
]