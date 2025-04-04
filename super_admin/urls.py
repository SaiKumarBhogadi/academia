from django.urls import path
from . import views

app_name = 'super_admin'
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('add-user/', views.add_user, name='add_user'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('toggle-user-active/<int:user_id>/', views.toggle_user_active, name='toggle_user_active'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
]