from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import StudentProfile
from .forms import StudentRegistrationForm, StudentProfileForm
from core.signals import user_registered
import logging
from colleges.utils import STATES_DISTRICTS

logger = logging.getLogger(__name__)

def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            user_registered.send(sender=None, user=user)
            messages.success(request, 'Registration successful! Please wait for admin approval.')
            logger.info("Student %s registered, awaiting approval", form.cleaned_data['username'])
            return redirect('core:login')
        else:
            messages.error(request, 'Please correct the errors below.')
            logger.warning("Student registration failed due to form errors: %s", form.errors)
    else:
        form = StudentRegistrationForm()
    return render(request, 'students/register.html', {
        'form': form,
        'states_districts': STATES_DISTRICTS
    })

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import StudentProfile
import logging

# Set up logging
logger = logging.getLogger(__name__)

@login_required
def student_profile(request):
    logger.debug(f"User: {request.user.username}, User Type: {request.user.user_type}, Approved: {request.user.is_approved}")
    
    if request.user.user_type != 'student':
        messages.error(request, "You are not authorized to access this page.")
        logger.warning(f"Non-student user {request.user.username} attempted to access student profile.")
        return redirect('core:login')
    
    if not request.user.is_approved:
        messages.error(request, "Your account is not yet approved by the super admin.")
        logger.warning(f"Unapproved user {request.user.username} attempted to access student profile.")
        return redirect('core:pending_approval')

    try:
        student_profile = StudentProfile.objects.select_related('user').get(user=request.user)
        logger.debug(f"Student profile found for user {request.user.username}")
    except StudentProfile.DoesNotExist:
        messages.error(request, "Profile not found. Please complete your registration or contact support.")
        logger.error(f"No StudentProfile found for user {request.user.username}")
        return redirect('core:pending_approval')
    except Exception as e:
        messages.error(request, "An error occurred while loading your profile.")
        logger.error(f"Unexpected error for user {request.user.username}: {str(e)}")
        return render(request, 'students/student_profile.html', {
            'error_message': f"Error: {str(e)}"
        })

    return render(request, 'students/student_profile.html', {
        'student_profile': student_profile,
        'debug_message': 'Profile loaded successfully'
    })

@login_required
def edit_student_profile(request):
    if request.user.user_type != 'student':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('core:login')
    
    if not request.user.is_approved:
        messages.error(request, "Your account is not yet approved by the super admin.")
        return redirect('core:pending_approval')

    try:
        student_profile = StudentProfile.objects.select_related('user').get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, "Profile not found. Contact support.")
        return redirect('core:pending_approval')

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=student_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('students:student_profile')
        else:
            messages.error(request, "Please correct the errors below.")
            logger.warning("Student profile update failed due to form errors: %s", form.errors)
    else:
        form = StudentProfileForm(instance=student_profile)

    return render(request, 'students/edit_student_profile.html', {
        'form': form,
        'student_profile': student_profile,
        'states_districts': STATES_DISTRICTS
    })


from core.forms import UserUpdateForm
@login_required
def update_student_details(request):
    if request.user.user_type != 'student':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('core:login')
    
    if not request.user.is_approved:
        messages.error(request, "Your account is not yet approved by the super admin.")
        return redirect('core:pending_approval')

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account details have been updated successfully.")
            return redirect('students:student_details_updated')
        else:
            messages.error(request, "Please correct the errors below.")
            logger.warning("Student details update failed due to form errors: %s", form.errors)
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'students/update_student_details.html', {'form': form})

@login_required
def student_details_updated(request):
    if request.user.user_type != 'student':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('core:login')
    return render(request, 'students/student_details_updated.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from schools.models import Admission, Seat
from colleges.models import Application  # Import Application model
import logging

logger = logging.getLogger(__name__)

@login_required
def student_dashboard(request):
    if request.user.user_type != 'student':
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    try:
        student_profile = request.user.student_profile
        admission_preference = student_profile.admission_preference
        logger.info("User %s has admission preference: %s", request.user.username, admission_preference)
    except StudentProfile.DoesNotExist:
        messages.warning(request, "Please create your profile and set your admission preference.")
        return redirect('students:student_profile')

    if not admission_preference:
        messages.warning(request, "Please set your admission preference (School or College) in your profile.")
        return redirect('students:student_profile')

    applications = []
    if admission_preference.lower() == 'school':
        applications = Admission.objects.filter(student=request.user).select_related(
            'school', 'school_class', 'section', 'seat'
        )
        logger.info("Fetched %d school applications for user %s", applications.count(), request.user.username)
    elif admission_preference.lower() == 'college':
        applications = Application.objects.filter(student=request.user).select_related(
            'department__college', 'section', 'seat'
        )
        logger.info("Fetched %d college applications for user %s", applications.count(), request.user.username)
        # Log details of applications
        for app in applications:
            logger.info("Application ID: %s, Institution: %s, Status: %s", app.id, app.department.college.college_name, app.status)

    formatted_applications = []
    for app in applications:
        if admission_preference.lower() == 'school':
            formatted_applications.append({
                'type': 'School',
                'id': app.id,
                'institution': app.school.school_name,
                'department_class': app.school_class.grade,
                'section': app.section.section_name if app.section else 'Not Assigned',
                'seat_number': app.seat.seat_number if app.seat else 'Not Assigned',
                'status': app.status,
                'date': app.admission_date,
                'can_withdraw': app.status in ['Pending', 'Approved'],
                'view_url': 'students:view_school_application',
            })
        else:
            formatted_applications.append({
                'type': 'College',
                'id': app.id,
                'institution': app.department.college.college_name,
                'department_class': app.department.name,
                'section': app.section.section_name if app.section else 'Not Assigned',
                'seat_number': app.seat.seat_number if app.seat else 'Not Assigned',
                'status': app.status,
                'date': app.apply_date,
                'can_withdraw': app.status in ['Pending', 'Approved'],
                'view_url': 'students:view_college_application_details',
            })

    context = {
        'applications': formatted_applications,
        'admission_preference': admission_preference,
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

# ... (previous views)
@login_required
def withdraw_application(request, application_id):
    if request.user.user_type != 'student':
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    try:
        admission_preference = request.user.student_profile.admission_preference
    except StudentProfile.DoesNotExist:
        messages.error(request, "Please create your student profile first.")
        return redirect('students:student_profile')

    if not admission_preference:
        messages.error(request, "Please set your admission preference in your profile.")
        return redirect('students:student_profile')

    logger.info("Processing withdraw request for application/admission with ID: %s for user: %s", application_id, request.user.username)
    
    application = None
    is_college_app = admission_preference == StudentProfile.AdmissionPreference.COLLEGE
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

    institution_name = application.department.college.college_name if is_college_app else application.school.school_name
    logger.debug("Fetched application/admission - ID: %s, Type: %s, Institution: %s, Status: %s, Section: %s", 
                 application.id, 'College' if is_college_app else 'School', institution_name, application.status,
                 application.section.section_name if hasattr(application, 'section') else 'N/A')

    context = {'application': application}
    if not is_college_app:
        context.update({
            'application': application,
            'department': type('obj', (object,), {'name': application.school_class.grade})(),
            'college': type('obj', (object,), {'college_name': application.school.school_name})()
        })

    if request.method == 'GET':
        return render(request, 'students/withdraw_application.html', context)

    if request.method == 'POST':
        logger.debug("Attempting to withdraw - Current status: %s", application.status)
        if application.status not in ['Pending', 'Approved']:
            logger.warning("Withdrawal attempt failed - Status: %s is not 'Pending' or 'Approved'", application.status)
            messages.error(request, f"You can only withdraw applications that are in 'Pending' or 'Approved' status. Current status: {application.status}")
            return redirect('students:student_dashboard')
        
        if application.seat:
            seat = application.seat
            seat.is_filled = False
            seat.student = None
            seat.save()
            application.seat = None
            logger.info("Freed seat for application/admission %s", application_id)
        
        institution = application.department.college if is_college_app else application.school
        if not institution:
            logger.warning("No valid institution found for application %s", application_id)
            messages.error(request, "Unable to process withdrawal due to missing institution.")
            return redirect('students:student_dashboard')

        application.status = 'Withdrawn'
        application.save()
        logger.info("Updated status to 'Withdrawn' for application/admission %s", application_id)
        
        application_withdrawn.send(
            sender=Application if is_college_app else Admission,
            student=request.user,
            school=institution,
            application=application
        )
        logger.info("Sent application_withdrawn signal for application/admission %s", application_id)

        messages.success(request, "Your application has been withdrawn successfully.")
        return redirect('students:student_dashboard')

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





from core.signals import profile_created, profile_updated, application_withdrawn, password_changed
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.http import HttpResponseForbidden
from django.http import HttpResponse    
import logging

logger = logging.getLogger(__name__)

@login_required
def my_applications(request):
    if not hasattr(request.user, 'student_profile'):
        messages.error(request, "Please create your student profile first.")
        return redirect('students:student_profile')
    
    admission_preference = request.user.student_profile.admission_preference
    logger.info("User %s has admission preference: %s", request.user.username, admission_preference)
    if not admission_preference:
        messages.error(request, "Please set your admission preference (School or College) in your profile.")
        return redirect('students:student_profile')

    # Handle case-insensitive comparison
    admission_preference_lower = admission_preference.lower() if admission_preference else None
    applications = []
    app_type = 'School' if admission_preference_lower == 'school' else 'College'
    
    if admission_preference_lower == 'school':
        applications = Admission.objects.filter(student=request.user).select_related(
            'school', 'school_class', 'section', 'seat'
        )
        logger.info("Fetched %d school admissions for user %s", applications.count(), request.user.username)
    else:
        applications = Application.objects.filter(student=request.user).select_related(
            'department__college', 'section', 'seat'
        )
        logger.info("Fetched %d college applications for user %s", applications.count(), request.user.username)

    all_applications = []
    for app in applications:
        if admission_preference_lower == 'school':
            all_applications.append({
                'id': app.id,
                'institution': app.school.school_name,
                'department_class': app.school_class.grade,
                'section': app.section.section_name if app.section else 'Not Assigned',
                'seat_number': app.seat.seat_number if app.seat else 'Not Assigned',
                'status': app.status,
                'date': app.admission_date,
                'can_withdraw': app.status in ['Pending', 'Approved'],
                'view_url': 'students:view_school_application',
            })
        else:
            all_applications.append({
                'id': app.id,
                'institution': app.department.college.college_name,
                'department_class': app.department.name,
                'section': app.section.section_name if app.section else 'Not Assigned',
                'seat_number': app.seat.seat_number if app.seat else 'Not Assigned',
                'status': app.status,
                'date': app.apply_date,
                'can_withdraw': app.status in ['Pending', 'Approved'],
                'view_url': 'students:view_college_application_details',
            })

    context = {
        'applications': all_applications,
        'app_type': app_type,
        'admission_preference': admission_preference,
    }
    return render(request, 'students/student_applications.html', context)

@login_required
def view_school_application(request, application_id):
    if not hasattr(request.user, 'student_profile'):
        return HttpResponseForbidden("You are not authorized to access this page as a student.")

    admission_preference = request.user.student_profile.admission_preference
    logger.info("Viewing school application %s for user %s with preference %s", application_id, request.user.username, admission_preference)

    # Handle case-insensitive comparison
    if admission_preference and admission_preference.lower() != 'school':
        messages.error(request, "You have selected College Admissions. Update your profile to view School Applications.")
        return redirect('students:student_profile')

    admission = get_object_or_404(Admission, id=application_id, student=request.user)
    logger.info("Fetched admission %s for user %s", admission.id, request.user.username)

    context = {
        'admission': admission,
        'school': admission.school,
        'app_type': 'School',
    }
    return render(request, 'students/view_school_application.html', context)

@login_required
def download_school_application(request, application_id):
    if not hasattr(request.user, 'student_profile'):
        return HttpResponseForbidden("You are not authorized to access this page as a student.")

    admission_preference = request.user.student_profile.admission_preference
    # Handle case-insensitive comparison
    if admission_preference and admission_preference.lower() != 'school':
        messages.error(request, "You have selected College Admissions. Update your profile to view School Applications.")
        return redirect('students:student_profile')

    admission = get_object_or_404(Admission, id=application_id, student=request.user)
    logger.info("Generating PDF for admission %s for user %s", admission.id, request.user.username)

    html_string = render_to_string('students/pdf_application_template.html', {
        'admission': admission,
        'school': admission.school,
    })

    try:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="application_{admission.admission_id}.pdf"'

        pisa_status = pisa.CreatePDF(
            html_string,
            dest=response,
            encoding='utf-8'
        )

        if pisa_status.err:
            logger.error("PDF generation failed for admission %s: %s", admission.id, pisa_status.err)
            messages.error(request, "Failed to generate PDF. Please try again later.")
            return render(request, 'students/view_school_application.html', {
                'admission': admission,
                'school': admission.school,
                'app_type': 'School',
            })

        return response
    except Exception as e:
        logger.error("PDF generation failed for admission %s: %s", admission.id, str(e))
        messages.error(request, "Failed to generate PDF. Please try again later.")
        return render(request, 'students/view_school_application.html', {
            'admission': admission,
            'school': admission.school,
            'app_type': 'School',
        })

@login_required
def view_application_details(request, application_id):
    if not hasattr(request.user, 'student_profile'):
        return HttpResponseForbidden("You are not authorized to access this page as a student.")

    admission_preference = request.user.student_profile.admission_preference
    logger.info("Viewing college application %s for user %s with preference %s", application_id, request.user.username, admission_preference)

    # Handle case-insensitive comparison
    if admission_preference and admission_preference.lower() != 'college':
        messages.error(request, "You have selected School Admissions. Update your profile to view College Applications.")
        return redirect('students:student_profile')

    application = get_object_or_404(Application, id=application_id, student=request.user)
    college = application.department.college
    logger.info("Viewing application details %s for user %s", application.id, request.user.username)

    context = {
        'application': application,
        'college': college,
        'app_type': 'College',
    }
    return render(request, 'students/view_application_details.html', context)

@login_required
def download_college_application(request, application_id):
    if not hasattr(request.user, 'student_profile'):
        return HttpResponseForbidden("You are not authorized to access this page as a student.")

    admission_preference = request.user.student_profile.admission_preference
    # Handle case-insensitive comparison
    if admission_preference and admission_preference.lower() != 'college':
        messages.error(request, "You have selected School Admissions. Update your profile to view College Applications.")
        return redirect('students:student_profile')

    application = get_object_or_404(Application, id=application_id, student=request.user)
    college = application.department.college
    logger.info("Generating PDF for application %s for user %s", application.id, request.user.username)

    html_string = render_to_string('students/college_pdf_application_template.html', {
        'application': application,
        'college': college,
    })

    try:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="application_{application.admission_id}.pdf"'

        pisa_status = pisa.CreatePDF(
            html_string,
            dest=response,
            encoding='utf-8'
        )

        if pisa_status.err:
            logger.error("PDF generation failed for application %s: %s", application.id, pisa_status.err)
            messages.error(request, "Failed to generate PDF. Please try again later.")
            return render(request, 'students/view_application_details.html', {
                'application': application,
                'college': college,
                'app_type': 'College',
            })

        return response
    except Exception as e:
        logger.error("PDF generation failed for application %s: %s", application.id, str(e))
        messages.error(request, "Failed to generate PDF. Please try again later.")
        return render(request, 'students/view_application_details.html', {
            'application': application,
            'college': college,
            'app_type': 'College',
        })