from django.urls import path
from . import views

app_name = 'schools'

urlpatterns = [
    path('dashboard/', views.school_dashboard, name='dashboard'),
    path('profile/', views.school_profile, name='school_profile'),
    path('class-section-management/', views.class_section_management, name='class_section_management'),
    path('admissions/', views.admissions, name='admissions'),
    path('apply/<int:school_id>/', views.apply_for_admission, name='apply_for_admission'),
    path('application-success/', views.application_success, name='application_success'),
    path('get-classes/', views.get_classes, name='get_classes'),
    path('get-sections/', views.get_sections, name='get_sections'),
    path('get-seats/', views.get_seats, name='get_seats'),
    path('school-list/', views.school_list, name='school_list'),
    path('school-seats/<int:school_id>/', views.school_seats, name='school_seats'),

    path('public-profile/<int:school_id>/', views.public_school_profile, name='public_school_profile'),
    path('change-password/', views.school_change_password, name='change_password'),
   

  


    # Other URL patterns...
    path('get-sections/<int:class_id>/', views.get_sections, name='get_sections'),
    path('get-seats/<int:section_id>/', views.get_seats, name='get_seats'),
    path('applications/', views.applications, name='applications'),
    path('application/<int:application_id>/details/', views.view_application_details, name='view_application_details'),
    path('student-details/<int:student_id>/', views.student_details, name='student_details'),


    path('create-cycle/', views.create_cycle, name='create_cycle'),
    path('edit-cycle/<int:cycle_id>/', views.edit_cycle, name='edit_cycle'),
    path('cycle-list/', views.cycle_list, name='cycle_list'),

    path('packages/', views.packages, name='packages'),
    
]
