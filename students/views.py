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
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from colleges.models import Application
from schools.models import Admission
from core.signals import application_withdrawn
import logging

logger = logging.getLogger(__name__)

@login_required
def withdraw_application(request, application_id):
    if request.user.user_type != 'student':
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    logger.info("Processing withdraw request for application/admission with ID: %s for user: %s", application_id, request.user.username)
    
    # Determine the context from the referrer URL (for GET) or form data (for POST)
    is_school_context = 'school/applications/' in request.META.get('HTTP_REFERER', '')
    if request.method == 'POST':
        is_school_context = request.POST.get('app_type') == 'School'

    # Try to get the correct model based on context
    application = None
    is_college_app = not is_school_context
    try:
        if is_college_app:
            application = Application.objects.get(id=application_id, student=request.user)
            logger.info("Found Application with ID %s, status: %s", application_id, application.status)
        else:
            application = Admission.objects.get(id=application_id, student=request.user)
            logger.info("Found Admission with ID %s, status: %s", application_id, application.status)
    except (Application.DoesNotExist, Admission.DoesNotExist):
        logger.error("No %s found for ID %s and user %s", 
                     "Application" if is_college_app else "Admission", application_id, request.user.username)
        messages.error(request, f"No {('application' if is_college_app else 'admission')} found with ID {application_id} for your account.")
        return redirect('students:student_dashboard')

    # Debug: Log the fetched application details
    institution_name = application.department.college.college_name if is_college_app else application.school.school_name
    logger.debug("Fetched application/admission - ID: %s, Type: %s, Institution: %s, Status: %s, Section: %s", 
                 application.id, 'College' if is_college_app else 'School', institution_name, application.status,
                 application.section.section_name if hasattr(application, 'section') else 'N/A')

    # Prepare context for template
    context = {'application': application}
    if not is_college_app:
        context.update({
            'application': application,
            'department': type('obj', (object,), {'name': application.school_class.grade})(),
            'college': type('obj', (object,), {'college_name': application.school.school_name})()
        })

    # Handle GET request (show confirmation)
    if request.method == 'GET':
        return render(request, 'students/withdraw_application.html', context)

    # Handle POST request (process withdrawal)
    if request.method == 'POST':
        # Log current status for debugging
        logger.debug("Attempting to withdraw - Current status: %s", application.status)
        # Check if the application can be withdrawn
        if application.status not in ['Pending', 'Approved']:
            logger.warning("Withdrawal attempt failed - Status: %s is not 'Pending' or 'Approved'", application.status)
            messages.error(request, f"You can only withdraw applications that are in 'Pending' or 'Approved' status. Current status: {application.status}")
            return redirect('students:student_dashboard')
        
        # Free up the seat if assigned
        if application.seat:
            seat = application.seat
            seat.is_filled = False
            seat.student = None
            seat.save()
            application.seat = None
            logger.info("Freed seat for application/admission %s", application_id)
        
        # Store the institution profile for the signal
        institution = application.department.college if is_college_app else application.school
        if not institution:
            logger.warning("No valid institution found for application %s", application_id)
            messages.error(request, "Unable to process withdrawal due to missing institution.")
            return redirect('students:student_dashboard')

        # Update the application status
        application.status = 'Withdrawn'
        application.save()
        logger.info("Updated status to 'Withdrawn' for application/admission %s", application_id)
        
        # Debug the signal data
        print(f"Triggering application_withdrawn signal - application_id: {application_id}, student: {request.user.email}, "
              f"institution: {institution}, is_college_app: {is_college_app}, application_type: {type(application).__name__}, "
              f"section: {getattr(application, 'section', None)}, school_class: {getattr(application, 'school_class', None)}")
        application_withdrawn.send(
            sender=Application if is_college_app else Admission,
            student=request.user,
            school=institution,
            application=application
        )
        logger.info("Sent application_withdrawn signal for application/admission %s", application_id)

        messages.success(request, "Your application has been withdrawn successfully. You can now apply to a different class or department.")
        return redirect('students:student_dashboard')

    # Invalid method
    messages.error(request, "Invalid request method.")
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





from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from colleges.models import Application
from schools.models import Admission
import logging

logger = logging.getLogger(__name__)

@login_required
def college_applications(request):
    if not hasattr(request.user, 'student_profile'):
        return HttpResponseForbidden("You are not authorized to access this page as a student.")
    
    college_applications = Application.objects.filter(student=request.user).select_related(
        'department__college', 'section', 'seat'
    )
    logger.info("Fetched %d college applications for user %s", college_applications.count(), request.user.username)

    all_applications = []
    for app in college_applications:
        all_applications.append({
            'type': 'College',
            'id': app.id,
            'institution': app.department.college.college_name,
            'department_class': app.department.name,
            'section': app.section.section_name if app.section else 'Not Assigned',
            'seat_number': app.seat.seat_number if app.seat else 'Not Assigned',
            'status': app.status,
            'date': app.apply_date,
            'can_withdraw': app.status in ['Pending', 'Approved']
        })
        if not app.section or not app.seat:
            logger.warning("Missing data for application %s: section=%s, seat=%s", app.id, app.section, app.seat)

    context = {
        'applications': all_applications,
        'app_type': 'College',
    }
    return render(request, 'students/student_applications.html', context)

@login_required
def school_applications(request):
    if not hasattr(request.user, 'student_profile'):
        return HttpResponseForbidden("You are not authorized to access this page as a student.")
    
    school_admissions = Admission.objects.filter(student=request.user).select_related(
        'school', 'school_class', 'section', 'seat'
    )
    logger.info("Fetched %d school admissions for user %s", school_admissions.count(), request.user.username)

    all_applications = []
    for adm in school_admissions:
        all_applications.append({
            'type': 'School',
            'id': adm.id,
            'institution': adm.school.school_name,
            'department_class': adm.school_class.grade,
            'section': adm.section.section_name if adm.section else 'Not Assigned',
            'seat_number': adm.seat.seat_number if adm.seat else 'Not Assigned',
            'status': adm.status,
            'date': adm.admission_date,
            'can_withdraw': adm.status in ['Pending', 'Approved']
        })
        if not adm.section or not adm.seat:
            logger.warning("Missing data for admission %s: section=%s, seat=%s", adm.id, adm.section, adm.seat)

    context = {
        'applications': all_applications,
        'app_type': 'School',
    }
    return render(request, 'students/student_applications.html', context)