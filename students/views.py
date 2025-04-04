from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from schools.models import Admission
from .models import StudentProfile
from .forms import StudentProfileForm

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from students.models import StudentProfile
from .forms import StudentProfileForm  # Assuming this is where your form is defined
from core.signals import profile_created, profile_updated  # Import the signals

@login_required
def student_profile(request):
    if request.user.user_type != 'student':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('core:login')

    try:
        student_profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        student_profile = None

    # Check if we're in edit mode
    edit_mode = request.GET.get('edit') == 'true'

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=student_profile)
        if form.is_valid():
            # Check if this is a new profile or an update
            is_new_profile = student_profile is None
            student_profile = form.save(commit=False)
            student_profile.user = request.user
            student_profile.save()
            # Trigger the appropriate signal
            if is_new_profile:
                profile_created.send(sender=None, user=request.user)
            else:
                profile_updated.send(sender=None, user=request.user)
            messages.success(request, "Profile created/updated successfully!")
            return redirect('students:student_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        if edit_mode and student_profile:
            form = StudentProfileForm(instance=student_profile)
        else:
            form = StudentProfileForm(instance=student_profile if student_profile else None)

    context = {
        'student_profile': student_profile if not edit_mode else None,
        'form': form,
    }
    return render(request, 'students/student_profile.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from schools.models import Admission, Seat  # Import from schools app

@login_required
def student_dashboard(request):
    if request.user.user_type != 'student':
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    applications = Admission.objects.filter(student=request.user)
    
    context = {
        'applications': applications,
    }
    return render(request, 'students/student_dashboard.html', context)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden
from schools.models import Admission, Seat
from core.signals import application_withdrawn  # Import the signal

@login_required
def withdraw_application(request, application_id):
    if request.user.user_type != 'student':
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # Get the application
    application = get_object_or_404(Admission, id=application_id, student=request.user)
    
    # Check if the application can be withdrawn
    if application.status != 'Pending':
        messages.error(request, "You can only withdraw applications that are in 'Pending' status.")
        return redirect('students:student_dashboard')
    
    # Withdraw the application
    if application.seat:
        # Free up the seat
        seat = application.seat
        seat.is_filled = False
        seat.student = None
        seat.save()
    
    # Store the school for the signal before modifying the application
    school = application.school.user

    # Update the application status
    application.status = 'Withdrawn'
    application.seat = None  # Remove the seat association
    application.save()
    
    # Trigger the application withdrawn signal
    application_withdrawn.send(
        sender=None,
        student=request.user,
        school=school,
        application=application
    )

    messages.success(request, "Your application has been withdrawn successfully. You can now apply to a different class.")
    return redirect('students:student_dashboard')


from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from core.signals import password_changed  # Import the signal

@login_required
def student_change_password(request):
    if request.user.user_type != 'student':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('core:home')

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)  # Update the session to keep the user logged in
            # Trigger the password_changed signal
            password_changed.send(
                sender=None,
                user=request.user
            )
            messages.success(request, "Your password has been successfully changed!")
            return redirect('students:student_profile')  # Redirect to student profile after success
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(user=request.user)

    context = {
        'form': form,
    }
    return render(request, 'students/change_password.html', context)