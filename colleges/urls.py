# colleges/urls.py
from django.urls import path
from . import views

app_name = 'colleges'

urlpatterns = [
    path('profile/', views.college_profile, name='college_profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # Degree management
    path('degrees/', views.degree_list, name='degree_list'),
    path('degrees/add/', views.add_degrees, name='add_degrees'),
    path('degrees/<int:degree_id>/edit/', views.edit_degree, name='edit_degree'),
    # Department management
    path('departments/', views.department_list, name='department_list'),
    path('degrees/<int:degree_id>/departments/add/', views.link_departments, name='link_departments'),
    path('degrees/<int:degree_id>/departments/<int:department_id>/edit/', views.edit_department, name='edit_department'),
    # Course management
    path('courses/', views.course_list_all, name='course_list_all'),
    path('degrees/<int:degree_id>/departments/<int:department_id>/courses/', views.course_list, name='course_list'),
    path('degrees/<int:degree_id>/departments/<int:department_id>/courses/add/', views.add_course, name='add_course'),
    path('degrees/<int:degree_id>/departments/<int:department_id>/courses/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    # Student-facing URLs
    path('college-list/', views.college_list, name='college_list'),
    path('<int:college_id>/', views.college_detail, name='college_detail'),
    path('<int:college_id>/degrees/<int:degree_id>/departments/', views.student_department_list, name='student_department_list'),
    path('<int:college_id>/degrees/<int:degree_id>/departments/<int:department_id>/', views.degree_detail, name='degree_detail'),
]