from django.dispatch import Signal, receiver
from core.utils import create_notification

# Define signals
password_changed = Signal()
profile_created = Signal()
profile_updated = Signal()
application_submitted = Signal()
application_status_updated = Signal()  
application_withdrawn = Signal()


# Signal handler for application withdrawal
@receiver(application_withdrawn)
def handle_application_withdrawn(sender, student, school, application, **kwargs):
    student_name = student.username or student.first_name or student.email or "Unknown Student"
    school_name = school.username or school.first_name or school.email or "Unknown School"
    class_grade = application.school_class.grade if application.school_class else "Unknown Class"
    create_notification(
        user=student,
        message=f"You have withdrawn your application to {school_name}.",
        notification_type='admission_update'
    )
    create_notification(
        user=school,
        message=f"{student_name} has withdrawn their application for Class {class_grade}.",
        notification_type='admission_update'
    )

# Signal handler for application submission
@receiver(application_submitted)
def handle_application_submitted(sender, student, school, application, **kwargs):
    # Use username, first_name, or email to avoid empty names
    student_name = student.username or student.first_name or student.email or "Unknown Student"
    school_name = school.username or school.first_name or school.email or "Unknown School"
    # Notification for the student
    create_notification(
        user=student,
        message=f"Your application to {school_name} has been submitted.",
        notification_type='admission_update'
    )
    # Notification for the school
    create_notification(
        user=school,
        message=f"A new application has been submitted by {student_name}.",
        notification_type='admission_update'
    )

# Signal handler for application status update
@receiver(application_status_updated)
def handle_application_status_updated(sender, student, school, application, **kwargs):
    student_name = student.username or student.first_name or student.email or "Unknown Student"
    school_name = school.username or school.first_name or school.email or "Unknown School"
    # Notification for the student
    create_notification(
        user=student,
        message=f"Your application to {school_name} has been {application.status.lower()}.",
        notification_type='admission_update'
    )
    # Notification for the school
    create_notification(
        user=school,
        message=f"You have updated the application status for {student_name} to {application.status.lower()}.",
        notification_type='admission_update'
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