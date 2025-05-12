from django.dispatch import Signal, receiver
from core.utils import create_notification

# Define signals
password_changed = Signal()
profile_created = Signal()
profile_updated = Signal()
application_submitted = Signal()
application_status_updated = Signal()  
application_withdrawn = Signal()


# In signals.py
@receiver(application_withdrawn)
def handle_application_withdrawn(sender, student, school, application, **kwargs):
    print(f"Handling application_withdrawn - student: {student.email}, school: {school}, application_id: {application.id}, sender: {sender.__name__}")
    student_name = student.username or student.first_name or student.email or "Unknown Student"
    try:
        if hasattr(school, 'college_name'):
            print("Detected college context")
            institution_name = school.college_name
            section_name = application.section.section_name if hasattr(application, 'section') and application.section else "Unknown Section"
            degree_name = application.department.degree.degree_name if hasattr(application, 'department') and application.department and hasattr(application.department, 'degree') else "Unknown Degree"
            department_name = application.department.name if hasattr(application, 'department') and application.department else "Unknown Department"
            college_name = institution_name
            school_name = None
            class_grade = None
        elif hasattr(school, 'school_name'):
            print("Detected school context")
            institution_name = school.school_name
            section_name = application.section.section_name if hasattr(application, 'section') and application.section else "Unknown Section"
            class_grade = application.school_class.grade if hasattr(application, 'school_class') and application.school_class else "Unknown Class"
            school_name = institution_name
            college_name = None
            degree_name = None
            department_name = None
        else:
            print("Unknown institution context")
            institution_name = school.username or school.email or "Unknown Institution"
            section_name = "Unknown Section/Class"
            college_name = None
            school_name = None
            degree_name = None
            department_name = None
            class_grade = None
    except (AttributeError, ObjectDoesNotExist) as e:
        institution_name = "Unknown Institution"
        section_name = "Unknown Section/Class"
        college_name = None
        school_name = None
        degree_name = None
        department_name = None
        class_grade = None
        print(f"Error in context: {str(e)}")

    # Notification for the student
    try:
        create_notification(
            user=student,
            message=f"You have withdrawn your application to {institution_name} (Section/Class: {section_name}).",
            notification_type='admission_update'
        )
        print("Notification created for student")
    except Exception as e:
        print(f"Failed to create notification for student: {str(e)}")

    # Email for the student
    print(f"Attempting email to student: {student.email}")
    try:
        send_email(
            subject="Application Withdrawn - Academia",
            template_prefix="application_withdrawn_student",
            context={
                'recipient_name': student_name,
                'institution_name': institution_name,
                'section_name': section_name,
                'college_name': college_name,
                'school_name': school_name,
                'degree_name': degree_name,
                'department_name': department_name,
                'class_grade': class_grade,
            },
            to_email=student.email
        )
        print(f"Email sent to student: {student.email}")
    except Exception as e:
        print(f"Failed to send email to student: {str(e)}")

    # Notification and email for the institution admin
    admin_user = school.user if hasattr(school, 'user') else school
    try:
        create_notification(
            user=admin_user,
            message=f"{student_name} has withdrawn their application for {section_name} at {institution_name}.",
            notification_type='admission_update'
        )
        print("Notification created for admin")
    except Exception as e:
        print(f"Failed to create notification for admin: {str(e)}")

    print(f"Attempting email to admin: {admin_user.email if hasattr(admin_user, 'email') else 'No email'}")
    try:
        send_email(
            subject="Application Withdrawn - Academia",
            template_prefix="application_withdrawn_admin",
            context={
                'recipient_name': admin_user.username or admin_user.email or "Admin",
                'student_name': student_name,
                'institution_name': institution_name,
                'section_name': section_name,
                'college_name': college_name,
                'school_name': school_name,
                'degree_name': degree_name,
                'department_name': department_name,
                'class_grade': class_grade,
            },
            to_email=admin_user.email if hasattr(admin_user, 'email') and admin_user.email else 'fallback@academiaadmit.in'
        )
        print(f"Email sent to admin: {admin_user.email if hasattr(admin_user, 'email') else 'fallback@academiaadmit.in'}")
    except Exception as e:
        print(f"Failed to send email to admin: {str(e)}")


# Signal handler for application submission
from django.dispatch import Signal, receiver
from core.utils import create_notification
from django.core.exceptions import ObjectDoesNotExist

# Define signals
password_changed = Signal()
profile_created = Signal()
profile_updated = Signal()
application_submitted = Signal()
application_status_updated = Signal()  
application_withdrawn = Signal()
section_seats_updated = Signal()  # New signal for seat changes

# Signal handler for application submission (generic for school or college)
@receiver(application_submitted)
def handle_application_submitted(sender, student, institution, application, **kwargs):
    student_name = student.username or student.first_name or student.email or "Unknown Student"
    # Determine institution name based on model type
    try:
        if hasattr(institution, 'college_name'):
            institution_name = institution.college_name  # For CollegeProfile
        elif hasattr(institution, 'school_name'):
            institution_name = institution.school_name  # For SchoolProfile
        else:
            institution_name = institution.username or institution.email or "Unknown Institution"
    except (AttributeError, ObjectDoesNotExist):
        institution_name = "Unknown Institution"

    section = application.section.section_name if application.section else "Unknown Section"
    # Notification for the student
    create_notification(
        user=student,
        message=f"Your application to {institution_name} (Section: {section}) has been submitted.",
        notification_type='admission_update'
    )
    # Notification for the institution admin (assuming a user field like institution.user)
    create_notification(
        user=institution.user if hasattr(institution, 'user') else institution,
        message=f"A new application has been submitted by {student_name} for Section {section}.",
        notification_type='admission_update'
    )

# ... (keep other handlers like application_withdrawn, application_status_updated, etc.)


application_status_updated = Signal()  


# Signal handler for application status update (generic for school or college)
# Handler for application status update (enhanced)
@receiver(application_status_updated)
def handle_application_status_updated(sender, student, institution, application, **kwargs):
    student_name = student.username or student.first_name or student.email or "Unknown Student"
    # Determine institution name based on model type
    try:
        if hasattr(institution, 'college_name'):
            institution_name = institution.college_name  # For CollegeProfile
            college_name = institution_name
            school_name = None
        elif hasattr(institution, 'school_name'):
            institution_name = institution.school_name  # For SchoolProfile
            school_name = institution_name
            college_name = None
        else:
            institution_name = institution.username or institution.email or "Unknown Institution"
            college_name = None
            school_name = None
    except (AttributeError, ObjectDoesNotExist):
        institution_name = "Unknown Institution"
        college_name = None
        school_name = None

    # Additional context
    section_name = application.section.section_name if hasattr(application, 'section') and application.section else "Unknown Section"
    class_grade = application.school_class.grade if hasattr(application, 'school_class') and application.school_class else None
    seat_number = application.seat.seat_number if application.seat else None

    # Notification for the student
    create_notification(
        user=student,
        message=f"Your application to {institution_name} has been {application.status.lower()}.",
        notification_type='admission_update'
    )
    # Email for the student
    print(f"Sending email to student: {student.email}")
    send_email(
        subject=f"Application Status Updated - Academia",
        template_prefix="application_status_updated_student",
        context={
            'recipient_name': student_name,
            'institution_name': institution_name,
            'status': application.status,
            'section_name': section_name,
            'class_grade': class_grade,
            'seat_number': seat_number,
            'college_name': college_name,
            'school_name': school_name,
        },
        to_email=student.email
    )

    # Notification and email for the institution admin
    admin_user = institution.user if hasattr(institution, 'user') else institution
    create_notification(
        user=admin_user,
        message=f"The application status for {student_name} at {institution_name} has been updated to {application.status.lower()}.",
        notification_type='admission_update'
    )
    print(f"Sending email to admin: {admin_user.email if hasattr(admin_user, 'email') else 'No email'}")
    send_email(
        subject=f"Application Status Updated - Academia",
        template_prefix="application_status_updated_admin",
        context={
            'recipient_name': admin_user.username or admin_user.email or "Admin",
            'student_name': student_name,
            'institution_name': institution_name,
            'status': application.status,
            'section_name': section_name,
            'class_grade': class_grade,
            'seat_number': seat_number,
            'college_name': college_name,
            'school_name': school_name,
        },
        to_email=admin_user.email if hasattr(admin_user, 'email') and admin_user.email else 'fallback@academiaadmit.in'  # Fallback email
    )

# Signal handler for password change
@receiver(password_changed)
def handle_password_changed(sender, user, **kwargs):
    create_notification(
        user=user,
        message="Your password was changed successfully.",
        notification_type='password_change'
    )

# Signal handler for profile creation
@receiver(profile_created)
def handle_profile_created(sender, user, **kwargs):
    create_notification(
        user=user,
        message="Your profile has been created successfully.",
        notification_type='profile_update'
    )

# Signal handler for profile update
@receiver(profile_updated)
def handle_profile_updated(sender, user, **kwargs):
    create_notification(
        user=user,
        message="Your profile has been updated successfully.",
        notification_type='profile_update'
    )


from django.dispatch import Signal, receiver
from core.utils import create_notification
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

# Define signals
user_registered = Signal()
# ... other signals ...

# Reusable email sending function
def send_email(subject, template_prefix, context, to_email):
    html_content = render_to_string(f'emails/{template_prefix}.html', context)
    text_content = render_to_string(f'emails/{template_prefix}.txt', context)
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    email.attach_alternative(html_content, "text/html")
    try:
        email.send()
        print(f"Email sent to {to_email} with subject: {subject}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {str(e)}")

# Handler for user registration
@receiver(user_registered)
def handle_user_registered(sender, user, **kwargs):
    user_name = user.username or user.first_name or user.email or "User"
    create_notification(
        user=user,
        message="Your account has been created successfully! Awaiting admin approval.",
        notification_type='account_update'
    )
    send_email(
        subject="Welcome to Academia - Account Created",
        template_prefix="user_registered",
        context={'recipient_name': user_name, 'login_url': 'http://academiaadmit.in/login'},  # Replace with your actual login URL
        to_email=user.email
    )


user_approved = Signal()
# Handler for user approval (new)
@receiver(user_approved)
def handle_user_approved(sender, user, **kwargs):
    user_name = user.username or user.first_name or user.email or "User"
    create_notification(
        user=user,
        message="Your account has been approved! You can now log in.",
        notification_type='account_update'
    )
    send_email(
        subject="Account Approved - Academia",
        template_prefix="user_approved",
        context={'recipient_name': user_name, 'login_url': 'http://academiaadmit.in/login'},  # Replace with your actual login URL
        to_email=user.email
    )



# Handler for application submission
@receiver(application_submitted)
def handle_application_submitted(sender, student, institution, application, **kwargs):
    student_name = student.username or student.first_name or student.email or "Unknown Student"
    try:
        if hasattr(institution, 'college_name'):
            institution_name = institution.college_name
            section_name = application.section.section_name if application.section else "Unknown Section"
        elif hasattr(institution, 'school_name'):
            institution_name = institution.school_name
            section_name = application.section.section_name if application.section else "Unknown Class/Section"  # Adjust if using ClassSection
        else:
            institution_name = institution.username or institution.email or "Unknown Institution"
            section_name = "Unknown Section"
    except (AttributeError, ObjectDoesNotExist):
        institution_name = "Unknown Institution"
        section_name = "Unknown Section"

    # Notification for the student
    create_notification(
        user=student,
        message=f"Your application to {institution_name} (Section: {section_name}) has been submitted.",
        notification_type='admission_update'
    )
    # Email for the student
    send_email(
        subject="Application Submitted - Academia",
        template_prefix="application_submitted_student",
        context={
            'recipient_name': student_name,
            'institution_name': institution_name,
            'section_name': section_name,
            'application_status': 'Pending',
        },
        to_email=student.email
    )

    # Notification and email for the institution admin
    admin_user = institution.user if hasattr(institution, 'user') else institution
    create_notification(
        user=admin_user,
        message=f"A new application has been submitted by {student_name} for {section_name} at {institution_name}.",
        notification_type='admission_update'
    )
    send_email(
        subject="New Application Submitted - Academia",
        template_prefix="application_submitted_admin",
        context={
            'recipient_name': admin_user.username or admin_user.email or "Admin",
            'student_name': student_name,
            'institution_name': institution_name,
            'section_name': section_name,
            'application_status': 'Pending',
        },
        to_email=admin_user.email
    )


from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from core.models import User

@receiver(user_logged_out)
def update_last_logout(sender, user, request, **kwargs):
    if user:
        user.last_logout = timezone.now()
        user.save()
