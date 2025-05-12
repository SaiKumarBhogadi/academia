from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'colleges'  # Namespace for the colleges app

urlpatterns = [
    # College Profile Management
     path('college-register/', views.college_register, name='college_register'),
    path('profile/', views.college_profile, name='college_profile'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Degree Management
    path('degrees/<int:degree_id>/edit/', views.edit_degree, name='edit_degree'),

    # Department Management
    path('departments/link/<int:degree_id>/', views.link_departments, name='link_departments'),
    path('departments/<int:degree_id>/<int:department_id>/edit/', views.edit_department, name='edit_department'),

    # Section Management
    path('sections/<int:department_id>/<int:section_id>/edit/', views.edit_section, name='edit_section'),
    path('sections/<int:department_id>/<int:section_id>/delete/', views.delete_section, name='delete_section'),
    path('sections/seats/<int:college_id>/<int:degree_id>/<int:department_id>/', views.section_seats, name='section_seats'),

    # Course Management
    path('courses/<int:degree_id>/<int:department_id>/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('courses/<int:degree_id>/<int:department_id>/', views.course_list, name='course_list'),
    path('courses/all/', views.course_list_all, name='course_list_all'),

    # Student-Facing Views
    path('', views.college_list, name='college_list'),  # Changed from 'colleges/'
    path('<int:college_id>/', views.college_detail, name='college_detail'),
    path('<int:college_id>/degrees/<int:degree_id>/departments/<int:cycle_id>/', views.student_department_list, name='student_department_list'),
    path('<int:college_id>/degrees/<int:degree_id>/departments/<int:department_id>/<int:cycle_id>/', views.degree_detail, name='degree_detail'),

    # Application Management
    path('departments/<int:college_id>/<int:degree_id>/<int:department_id>/seats/', views.department_seats, name='department_seats'),
    path('application/success/', views.application_success, name='application_success'),
    path('manage-applications/<int:college_id>/', views.manage_applications, name='manage_applications'),
    path('students/<int:college_id>/<int:student_id>/', views.college_student_details, name='college_student_details'),

    # Password Management
    path('change-password/', views.college_change_password, name='change_password'),

    # Direct Application
    path('apply/<int:college_id>/', views.apply_direct, name='apply_direct'),

    # AJAX Endpoints
    path('ajax/get_departments/', views.get_departments, name='get_departments'),
    path('ajax/get_sections/', views.get_sections, name='get_sections'),
    path('get_degrees/', views.get_degrees, name='get_degrees'),

    # Cycle, Degree, Department, Section, Course Management (New Views)
    path('cycles/', views.cycle_list, name='cycle_list'),
    path('cycles/add/', views.add_cycle, name='add_cycle'),
    path('cycles/<int:cycle_id>/edit/', views.edit_cycle, name='edit_cycle'),
    path('cycles/<int:cycle_id>/delete/', views.delete_cycle, name='delete_cycle'),
    path('degrees/', views.degree_list, name='degree_list'),
    path('degrees/add/', views.add_degree, name='add_degree'),
     path('degrees/delete/<int:degree_id>/', views.delete_degree, name='delete_degree'),
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/<int:degree_id>/', views.add_department, name='add_department'),
    path('departments/edit/<int:department_id>/', views.edit_department, name='edit_department'),
     path('departments/delete/<int:department_id>/', views.delete_department, name='delete_department'),
    path('sections/<int:department_id>/', views.section_list, name='section_list'),
    path('sections/add/<int:department_id>/', views.add_section, name='add_section'),
    path('courses/', views.course_list_all, name='course_list_all'),
    path('courses/add/<int:degree_id>/<int:department_id>/', views.add_course, name='add_course'),
    path('courses/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('courses/delete/<int:course_id>/', views.delete_course, name='delete_course'),
     path('packages/', views.packages, name='packages'),
     path('college/<int:college_id>/application/<int:application_id>/', views.view_application_details, name='view_application_details'),
     path('edit_profile/', views.edit_college_profile, name='edit_college_profile'),



      path('update-details/', views.update_college_details, name='update_college_details'),
    path('details-updated/', views.college_details_updated, name='college_details_updated'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])