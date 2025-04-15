# from django.shortcuts import render, redirect
# from django.contrib import messages
# from .forms import RegistrationForm

# def home(request):
#     return render(request, 'core/home.html')

# def register(request):
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             messages.success(request, 'Registration successful! Awaiting admin approval.')
#             return redirect('core:login')
#     else:
#         form = RegistrationForm()
#     return render(request, 'core/register.html', {'form': form})


from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User
from .forms import RegistrationForm, LoginForm
from django.db import IntegrityError

def home(request):
    return render(request, 'core/home.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from .forms import RegistrationForm
from core.signals import user_registered

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, 'Registration successful! Awaiting admin approval.')
                user_registered.send(sender=None, user=user)
                return redirect('core:login')
            except IntegrityError:
                messages.error(request, 'Username or email already exists. Please choose a different one.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()
    return render(request, 'core/register.html', {'form': form})


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import LoginForm
from .models import User  # Assuming your custom User model is in core/models.py

def custom_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['password']

            try:
                if '@' in identifier:
                    user = User.objects.get(email=identifier)
                else:
                    user = User.objects.get(username=identifier)
            except User.DoesNotExist:
                messages.error(request, 'Invalid credentials.')
                return render(request, 'core/login.html', {'form': form})

            # Check if the user is deactivated before authenticating
            if not user.is_active:
                messages.error(request, 'Your account has been deactivated.')
                return render(request, 'core/login.html', {'form': form})

            # Authenticate the user (this will check the password)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                if user.is_approved or user.user_type == 'super_admin':
                    login(request, user)
                    if user.user_type == 'super_admin':
                        return redirect('super_admin:dashboard')
                    elif user.user_type == 'school':
                        return redirect('schools:dashboard')
                    elif user.user_type == 'college':
                        return redirect('colleges:dashboard')
                    else:
                        return redirect('students:student_dashboard')
                else:
                    messages.error(request, 'Your account is not yet approved.')
            else:
                messages.error(request, 'Invalid credentials.')
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})


def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('core:home')

def student_dashboard(request):
    if request.user.user_type != 'student':
        return redirect('core:login')
    return render(request, 'core/student_dashboard.html')

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from core.models import Notification

@login_required
def mark_notification_read(request):
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            messages.success(request, "Notification marked as read.")
        except Notification.DoesNotExist:
            messages.error(request, "Notification not found.")
    
    # Redirect back to the current page
    return redirect(request.META.get('HTTP_REFERER', 'core:home'))


from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from core.models import Notification

@login_required
def mark_all_notifications_read(request):
    if request.method == 'POST':
        # Mark all unread notifications for the current user as read
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
        unread_notifications.update(is_read=True)
        messages.success(request, "All notifications have been marked as read.")
    return redirect(request.META.get('HTTP_REFERER', 'core:home'))


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.models import Notification

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import Notification

@login_required
def notifications(request):
    """Display notifications based on user type with dynamic base template"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Determine base template based on user type
    base_templates = {
        'super_admin': 'super_admin/base.html',
        'school': 'schools/base.html',
        'college': 'colleges/base.html',
        'student': 'students/base.html',
    }
    
    base_template = base_templates.get(request.user.user_type, 'base.html')  # Default to 'base.html' if no match

    context = {
        'notifications': notifications,
        'base_template': base_template
    }
    return render(request, 'core/notifications.html', context)
