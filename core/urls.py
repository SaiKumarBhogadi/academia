from django.urls import path
from .views import register
from . import views

app_name = 'core'
urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('mark-notification-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/', views.notifications, name='notifications'),
    path('mark-all-notifications-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    
    
]
