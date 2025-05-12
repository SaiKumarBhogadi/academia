from django.urls import path

from . import views

app_name = 'core'
urlpatterns = [
    path('', views.home, name='home'),
    # path('register/', views.register, name='register'),
    path('register-options/', views.register_options, name='register_options'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('mark-notification-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/', views.notifications, name='notifications'),
    path('mark-all-notifications-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('clients/',views.clients, name='clients'),
    path('testimonials/',views.testimonials, name='testimonials'),
    path('contact/',views.contact, name='contact'),

  path('online_admission/', views.online_admission, name='online_admission'),
    path('get_districts/', views.get_districts, name='get_districts'),
    path('get_institutions/', views.get_institutions, name='get_institutions'),
    path('admission_form/<str:institution_type>/<int:institution_id>/', views.admission_form, name='admission_form'),  

   


    
 path('password-reset/', views.password_reset_request_view, name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('password-reset/success/', views.password_reset_done_view, name='password_reset_success'),

    path('view-all-schools/', views.view_all_schools, name='view_all_schools'),
    path('institution/college/<int:id>/', views.college_detail, name='college_detail'),
    path('institution/school/<int:id>/', views.school_detail, name='school_detail'),
     
    
    
]
