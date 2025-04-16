import logging
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from .models import SchoolProfile, SchoolClass, Admission, ClassSection

# Set up logging
logger = logging.getLogger(__name__)

@login_required
def school_dashboard(request):
    # Check if the user is a school user and is approved
    if request.user.user_type != 'school':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('core:login')
    
    if not request.user.is_approved:
        messages.error(request, "Your account is not yet approved by the super admin.")
        return redirect('core:login')

    # Fetch the user's SchoolProfile (if it exists)
    try:
        school_profile = request.user.school_profile
    except SchoolProfile.DoesNotExist:
        school_profile = None

    # Fetch data for the dashboard
    school = school_profile
    if school:
        # Total admitted students
        total_admitted = Admission.objects.filter(school=school, status='Approved').count()
        
        # Pending applications
        pending_applications = Admission.objects.filter(school=school, status='Pending').count()
        
        # Total classes and sections
        total_classes = SchoolClass.objects.filter(school=school).count()
        total_sections = ClassSection.objects.filter(school_class__school=school).count()
        
        # Seat availability summary
        sections = ClassSection.objects.filter(school_class__school=school).prefetch_related('seats')
        total_seats = sum(section.total_seats for section in sections)
        filled_seats = sum(section.seats.filter(is_filled=True).count() for section in sections)
        available_seats = total_seats - filled_seats
        
        # Data for seat availability chart (per class)
        classes = SchoolClass.objects.filter(school=school).prefetch_related('sections__seats')
        chart_data = {
            'labels': [],
            'filled_seats': [],
            'available_seats': [],
        }
        for school_class in classes:
            class_filled_seats = 0
            class_total_seats = 0
            for section in school_class.sections.all():
                class_filled_seats += section.seats.filter(is_filled=True).count()
                class_total_seats += section.total_seats
            class_available_seats = class_total_seats - class_filled_seats
            chart_data['labels'].append(school_class.grade)  # Changed from "Class {school_class.grade}" to "Grade {school_class.grade}"
            chart_data['filled_seats'].append(class_filled_seats)
            chart_data['available_seats'].append(class_available_seats)
        
        # Log the chart_data to debug
        logger.info(f"Chart Data: {chart_data}")
        
        # Recent activity (e.g., recent applications)
        recent_applications = Admission.objects.filter(school=school).order_by('-admission_date')[:5]
    else:
        total_admitted = 0
        pending_applications = 0
        total_classes = 0
        total_sections = 0
        total_seats = 0
        filled_seats = 0
        available_seats = 0
        chart_data = {'labels': [], 'filled_seats': [], 'available_seats': []}
        recent_applications = []

    context = {
        'school_profile': school_profile,
        'total_admitted': total_admitted,
        'pending_applications': pending_applications,
        'total_classes': total_classes,
        'total_sections': total_sections,
        'total_seats': total_seats,
        'filled_seats': filled_seats,
        'available_seats': available_seats,
        'chart_data': chart_data,
        'recent_applications': recent_applications,
    }
    return render(request, 'schools/school_dashboard.html', context)



# schools/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import SchoolProfile, SchoolRating
from .forms import SchoolProfileForm, SchoolRatingForm

def rating_view(request, school_profile):
    # Fetch the rating (if it exists)
    rating = getattr(school_profile, 'rating', None)
    
    # Check if the user wants to edit the rating
    show_rating_form = request.GET.get('edit_rating') == 'true'
    
    # Handle form submission
    if request.method == 'POST' and 'form_type' in request.POST and request.POST['form_type'] == 'rating':
        rating_form = SchoolRatingForm(request.POST, instance=rating)
        if rating_form.is_valid():
            rating = rating_form.save(commit=False)
            rating.school_profile = school_profile
            rating.save()
            messages.success(request, "Rating updated successfully!")
            return {
                'redirect': redirect('schools:school_profile')  # Redirect to profile page (no edit mode)
            }
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        rating_form = SchoolRatingForm(instance=rating)
    
    # Calculate rating_int, decimal_part, and fill_width if rating exists
    rating_int = None
    decimal_part = None
    fill_width = None
    if rating:
        rating_value = float(rating.rating)  # e.g., 4.3
        rating_int = int(rating_value)  # e.g., 4
        decimal_part = rating_value - rating_int  # e.g., 0.3
        fill_width = decimal_part * 100  # e.g., 30.0 (for 30%)
    
    # Return context for the rating section
    return {
        'rating': rating,
        'rating_form': rating_form,
        'show_rating_form': show_rating_form,
        'rating_int': rating_int,
        'decimal_part': decimal_part,
        'fill_width': fill_width,
    }





from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from schools.models import SchoolProfile
from .forms import SchoolProfileForm
# from .views import rating_view, gallery_view, testimonial_view
from core.signals import profile_created, profile_updated

@login_required
def school_profile(request):
    # Check if the user is a school user and is approved
    if request.user.user_type != 'school':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('core:login')
    
    if not request.user.is_approved:
        messages.error(request, "Your account is not yet approved by the super admin.")
        return redirect('core:login')

    # Fetch the user's SchoolProfile with related fields (if any)
    try:
        school_profile = SchoolProfile.objects.select_related('user').get(user=request.user)
    except SchoolProfile.DoesNotExist:
        school_profile = None

    # Check if the user wants to edit the profile
    is_edit_mode = request.GET.get('edit') == 'true'

    # Handle form submission for the profile
    if request.method == 'POST' and 'form_type' in request.POST and request.POST['form_type'] == 'profile':
        form = SchoolProfileForm(request.POST, request.FILES, instance=school_profile)
        if form.is_valid():
            # Check if this is a new profile or an update
            is_new_profile = school_profile is None
            school_profile = form.save(commit=False)
            school_profile.user = request.user
            school_profile.save()
            # Trigger the appropriate signal
            if is_new_profile:
                profile_created.send(sender=None, user=request.user)
            else:
                profile_updated.send(sender=None, user=request.user)
            messages.success(request, "Profile updated successfully!")
            return redirect('schools:school_profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SchoolProfileForm(instance=school_profile)

    # Decide whether to show the form
    show_form = (school_profile is None) or is_edit_mode

    # Get the rating, gallery, and testimonial contexts (only if a school profile exists)
    rating_context = {}
    gallery_context = {}
    testimonial_context = {}
    if school_profile:
        # Defer heavy operations if possible
        rating_context = rating_view(request, school_profile)
        if 'redirect' in rating_context:
            return rating_context['redirect']
        
        gallery_context = gallery_view(request, school_profile)
        if 'redirect' in gallery_context:
            return gallery_context['redirect']
        
        testimonial_context = testimonial_view(request, school_profile)
        if 'redirect' in testimonial_context:
            return testimonial_context['redirect']

    # Combine all context data
    context = {
        'school_profile': school_profile,
        'form': form,
        'show_form': show_form,
    }
    context.update(rating_context)
    context.update(gallery_context)
    context.update(testimonial_context)

    return render(request, 'schools/school_profile.html', context)


def public_school_profile(request, school_id):
    # Fetch the school profile by ID
    school_profile = get_object_or_404(SchoolProfile, id=school_id)

    # Get the rating, gallery, and testimonial contexts
    rating_context = rating_view(request, school_profile)
    if 'redirect' in rating_context:
        return rating_context['redirect']
    
    gallery_context = gallery_view(request, school_profile)
    if 'redirect' in gallery_context:
        return gallery_context['redirect']
    
    testimonial_context = testimonial_view(request, school_profile)
    if 'redirect' in testimonial_context:
        return testimonial_context['redirect']

    # Combine all context data
    context = {
        'school_profile': school_profile,
    }
    context.update(rating_context)
    context.update(gallery_context)
    context.update(testimonial_context)

    return render(request, 'schools/public_profile.html', context)





from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
import os
from .models import SchoolGallery
from .forms import SchoolGalleryForm

def gallery_view(request, school_profile):
    # Fetch all gallery images for the school
    gallery_images = SchoolGallery.objects.filter(school_profile=school_profile).order_by('-uploaded_at')
    print(f"Gallery images count: {gallery_images.count()}")  # Debug

    # Check if the user wants to edit the gallery
    is_edit_mode = request.GET.get('edit_gallery') == 'true'
    print(f"Edit mode: {is_edit_mode}")  # Debug

    # Handle image upload
    if request.method == 'POST' and request.POST.get('action') == 'upload':
        print("Handling image upload")  # Debug
        form = SchoolGalleryForm(request.POST, request.FILES)
        if form.is_valid():
            gallery_image = form.save(commit=False)
            gallery_image.school_profile = school_profile
            gallery_image.save()
            messages.success(request, "Image uploaded successfully!")
            return {'redirect': redirect('schools:school_profile')}
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SchoolGalleryForm()

    # Handle image deletion
    if request.method == 'POST' and request.POST.get('action') == 'delete':
        print("Handling image deletion")  # Debug
        image_id = request.POST.get('image_id')
        print(f"Image ID to delete: {image_id}")  # Debug
        image = get_object_or_404(SchoolGallery, id=image_id, school_profile=school_profile)
        if image.image and os.path.isfile(image.image.path):
            os.remove(image.image.path)
            print(f"Deleted file: {image.image.path}")  # Debug
        image.delete()
        messages.success(request, "Image deleted successfully!")
        return {'redirect': redirect('schools:school_profile')}

    # Return context if no redirect
    return {
        'gallery_images': gallery_images,
        'gallery_form': form,
        'show_gallery_form': is_edit_mode,
    }



from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import SchoolTestimonial
from .forms import SchoolTestimonialForm

def testimonial_view(request, school_profile):
    # Fetch all testimonials for the school
    testimonials = SchoolTestimonial.objects.filter(school_profile=school_profile).order_by('-created_at')
    print(f"Testimonials count: {testimonials.count()}")  # Debug

    # Check if the user wants to edit the testimonials
    is_edit_mode = request.GET.get('edit_testimonials') == 'true'
    print(f"Edit testimonials mode: {is_edit_mode}")  # Debug

    # Handle testimonial submission
    if request.method == 'POST' and request.POST.get('action') == 'add_testimonial':
        print("Handling testimonial submission")  # Debug
        form = SchoolTestimonialForm(request.POST)
        if form.is_valid():
            testimonial = form.save(commit=False)
            testimonial.school_profile = school_profile
            testimonial.save()
            messages.success(request, "Testimonial added successfully!")
            return {'redirect': redirect('schools:school_profile')}
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SchoolTestimonialForm()

    # Handle testimonial deletion
    if request.method == 'POST' and request.POST.get('action') == 'delete_testimonial':
        print("Handling testimonial deletion")  # Debug
        testimonial_id = request.POST.get('testimonial_id')
        print(f"Testimonial ID to delete: {testimonial_id}")  # Debug
        testimonial = get_object_or_404(SchoolTestimonial, id=testimonial_id, school_profile=school_profile)
        testimonial.delete()
        messages.success(request, "Testimonial deleted successfully!")
        return {'redirect': redirect('schools:school_profile')}

    # Return context if no redirect
    return {
        'testimonials': testimonials,
        'testimonial_form': form,
        'show_testimonial_form': is_edit_mode,
    }





from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash  # Import this to update the session
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from core.signals import password_changed  # Import the signal

@login_required
def school_change_password(request):
    if request.user.user_type != 'school':
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
            return redirect('schools:dashboard')  # Redirect to school dashboard after success
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(user=request.user)

    context = {
        'form': form,
    }
    return render(request, 'schools/change_password.html', context)






from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import SchoolProfile, AdmissionCycle, SchoolClass, ClassSection, Seat
from .forms import SchoolClassForm, ClassSectionForm
import logging

logger = logging.getLogger(__name__)

@login_required
def class_section_management(request):
    if request.user.user_type != 'school':
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    try:
        school = SchoolProfile.objects.get(user=request.user)
        classes = SchoolClass.objects.filter(school=school).prefetch_related('sections__seats')
        cycles = AdmissionCycle.objects.filter(school=school).order_by('-year')
    except SchoolProfile.DoesNotExist:
        school = None
        classes = []
        cycles = []

    # Calculate filled_seats and available_seats dynamically for each section
    for school_class in classes:
        for section in school_class.sections.all():
            section.filled_seats_dynamic = section.seats.filter(is_filled=True).count()
            section.available_seats_dynamic = section.total_seats - section.filled_seats_dynamic

    # Initialize forms
    class_form = SchoolClassForm(request.POST if 'add_class' in request.POST else None)
    section_form = ClassSectionForm(request.POST if 'add_section' in request.POST else None)
    edit_class_form = None
    edit_section_form = None

    # Handle Form Submissions
    if request.method == 'POST':
        if 'add_class' in request.POST:
            if school is None:
                messages.error(request, "Please set up your school profile first.")
                return redirect('schools:class_section_management')
            if class_form.is_valid():
                grade = class_form.cleaned_data['grade']
                cycle_id = request.POST.get('cycle')
                try:
                    cycle = AdmissionCycle.objects.get(id=cycle_id, school=school)
                    if SchoolClass.objects.filter(school=school, grade=grade, cycle=cycle).exists():
                        class_form.add_error('grade', "This grade already exists for the selected cycle.")
                    else:
                        school_class = class_form.save(commit=False)
                        school_class.school = school
                        school_class.cycle = cycle
                        school_class.save()
                        logger.info(f"Added class {grade} for cycle {cycle.year} and school {school.id}")
                        messages.success(request, f"Class {grade} added successfully.")
                        return redirect('schools:class_section_management')
                except AdmissionCycle.DoesNotExist:
                    class_form.add_error(None, "Invalid cycle selected.")
            else:
                logger.warning(f"Class form invalid: {class_form.errors}")

        elif 'edit_class' in request.POST:
            if school is None:
                return redirect('schools:class_section_management')
            class_id = request.POST.get('class_id')
            school_class = get_object_or_404(SchoolClass, id=class_id, school=school)
            edit_class_form = SchoolClassForm(request.POST, instance=school_class)
            if edit_class_form.is_valid():
                cycle_id = request.POST.get('cycle')
                if cycle_id and school_class.cycle_id != int(cycle_id):
                    try:
                        school_class.cycle = AdmissionCycle.objects.get(id=cycle_id, school=school)
                    except AdmissionCycle.DoesNotExist:
                        edit_class_form.add_error(None, "Invalid cycle selected.")
                edit_class_form.save()
                logger.info(f"Edited class {school_class.grade} for school {school.id}")
                messages.success(request, f"Class {school_class.grade} updated successfully.")
                return redirect('schools:class_section_management')

        elif 'add_section' in request.POST:
            if school is None:
                messages.error(request, "Please set up your school profile first.")
                return redirect('schools:class_section_management')
            if section_form.is_valid():
                class_id = request.POST.get('class_id')
                cycle_id = request.POST.get('cycle')
                try:
                    school_class = SchoolClass.objects.get(id=class_id, school=school)
                    cycle = AdmissionCycle.objects.get(id=cycle_id, school=school)
                    if school_class.cycle != cycle:
                        section_form.add_error(None, "The selected class does not belong to the selected cycle.")
                    else:
                        section_name = section_form.cleaned_data['section_name']
                        if ClassSection.objects.filter(school_class=school_class, section_name=section_name, cycle=cycle).exists():
                            section_form.add_error('section_name', "This section name already exists for the selected class and cycle.")
                        else:
                            section = section_form.save(commit=False)
                            section.school_class = school_class
                            section.cycle = cycle
                            section.save()
                            total_seats = section.total_seats
                            for i in range(1, total_seats + 1):
                                seat_number = f"{section.section_name}{i}"
                                Seat.objects.create(section=section, seat_number=seat_number, is_filled=False)
                            logger.info(f"Added section {section_name} for class {school_class.grade} and cycle {cycle.year}")
                            messages.success(request, f"Section {section_name} added successfully.")
                            return redirect('schools:class_section_management')
                except SchoolClass.DoesNotExist:
                    section_form.add_error(None, "Invalid class selected.")
                except AdmissionCycle.DoesNotExist:
                    section_form.add_error(None, "Invalid cycle selected.")
            else:
                logger.warning(f"Section form invalid: {section_form.errors}")

        elif 'edit_section' in request.POST:
            if school is None:
                return redirect('schools:class_section_management')
            section_id = request.POST.get('section_id')
            section = get_object_or_404(ClassSection, id=section_id, school_class__school=school)
            old_total_seats = section.total_seats
            edit_section_form = ClassSectionForm(request.POST, instance=section)
            if edit_section_form.is_valid():
                cycle_id = request.POST.get('cycle')
                if cycle_id and section.cycle_id != int(cycle_id):
                    try:
                        section.cycle = AdmissionCycle.objects.get(id=cycle_id, school=school)
                    except AdmissionCycle.DoesNotExist:
                        edit_section_form.add_error(None, "Invalid cycle selected.")
                section = edit_section_form.save()
                new_total_seats = section.total_seats
                current_seats = section.seats.count()
                if new_total_seats > current_seats:
                    for i in range(current_seats + 1, new_total_seats + 1):
                        seat_number = f"{section.section_name}{i}"
                        Seat.objects.create(section=section, seat_number=seat_number, is_filled=False)
                elif new_total_seats < current_seats:
                    seats_to_remove = section.seats.filter(is_filled=False).order_by('-id')[:current_seats - new_total_seats]
                    for seat in seats_to_remove:
                        seat.delete()
                logger.info(f"Edited section {section.section_name} for class {section.school_class.grade}")
                messages.success(request, f"Section {section.section_name} updated successfully.")
                return redirect('schools:class_section_management')

        elif 'delete_section' in request.POST:
            if school is None:
                return redirect('schools:class_section_management')
            section_id = request.POST.get('section_id')
            section = get_object_or_404(ClassSection, id=section_id, school_class__school=school)
            section_name = section.section_name
            section.seats.all().delete()
            section.delete()
            logger.info(f"Deleted section {section_name} for school {school.id}")
            messages.success(request, f"Section {section_name} deleted successfully.")
            return redirect('schools:class_section_management')

        elif 'delete_class' in request.POST:
            if school is None:
                return redirect('schools:class_section_management')
            class_id = request.POST.get('class_id')
            school_class = get_object_or_404(SchoolClass, id=class_id, school=school)
            grade = school_class.grade
            for section in school_class.sections.all():
                section.seats.all().delete()
            school_class.sections.all().delete()
            school_class.delete()
            logger.info(f"Deleted class {grade} for school {school.id}")
            messages.success(request, f"Class {grade} deleted successfully.")
            return redirect('schools:class_section_management')

    context = {
        'school': school,
        'classes': classes,
        'class_form': class_form,
        'section_form': section_form,
        'edit_class_form': edit_class_form,
        'edit_section_form': edit_section_form,
        'cycles': cycles,
    }
    return render(request, 'schools/class_section_management.html', context)


from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.db import transaction, IntegrityError
from schools.models import SchoolProfile, SchoolClass, ClassSection, Seat, Admission, AdmissionCycle
from .forms import AdmissionForm

@login_required
def admissions(request):
    if request.user.user_type != 'school':
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # Try to get the SchoolProfile, but don't raise 404 if it doesn't exist
    try:
        school = SchoolProfile.objects.get(user=request.user)
        # Fetch all cycles for the school
        cycles = AdmissionCycle.objects.filter(school=school).order_by('-year')
        # Organize classes by cycle without filters
        cycle_classes = []
        for cycle in cycles:
            classes = SchoolClass.objects.filter(school=school, cycle=cycle).prefetch_related('sections__seats')
            if classes.exists():
                for school_class in classes:
                    for section in school_class.sections.all():
                        section.total_seats_dynamic = section.seats.count()
                        section.filled_seats_dynamic = section.seats.filter(is_filled=True).count()
                cycle_classes.append({'cycle': cycle, 'classes': classes})
    except SchoolProfile.DoesNotExist:
        school = None
        cycles = []
        cycle_classes = []

    # Fetch pending applications for this school
    pending_applications = Admission.objects.filter(
        school=school,
        status='Pending'
    ).select_related('student', 'school_class', 'section', 'seat')

    admission_form = AdmissionForm(request.POST or None)
    if request.method == 'POST' and 'admit_student' in request.POST:
        if school is None:
            messages.error(request, "Please set up your school profile to admit students.")
            return redirect('schools:admissions')
        if admission_form.is_valid():
            seat_id = request.POST.get('seat_id')
            section_id = request.POST.get('section_id')
            class_id = request.POST.get('class_id')

            seat = get_object_or_404(Seat, id=seat_id, section__id=section_id)
            section = get_object_or_404(ClassSection, id=section_id, school_class__id=class_id)
            school_class = get_object_or_404(SchoolClass, id=class_id, school=school)

            # Check if the student already has an approved admission in ANY class of this school
            student = admission_form.cleaned_data['student']
            existing_admission = Admission.objects.filter(
                student=student,
                school=school,
                status='Approved'
            ).exists()
            if existing_admission:
                messages.error(request, "This student is already admitted to a class in this school. A student can only be admitted to one class per school.")
                return redirect('schools:admissions')

            # Use a transaction to prevent race conditions
            try:
                with transaction.atomic():
                    # Lock the seat to prevent concurrent updates
                    seat = Seat.objects.select_for_update().get(id=seat_id, section__id=section_id)
                    if seat.is_filled:
                        messages.error(request, "The selected seat is already taken.")
                        return redirect('schools:admissions')

                    # Check if the seat is already assigned to another admission
                    if Admission.objects.filter(seat=seat, status='Approved').exists():
                        messages.error(request, "The selected seat is already assigned to another student.")
                        return redirect('schools:admissions')

                    # Create the admission
                    admission = admission_form.save(commit=False)
                    admission.school = school
                    admission.school_class = school_class
                    admission.section = section
                    admission.seat = seat
                    admission.status = 'Approved'
                    admission.save()

                    # Update the seat
                    seat.is_filled = True
                    seat.student = admission.student
                    seat.save()

                    # Update the section (use the dynamic count instead of the field)
                    section.filled_seats = section.seats.filter(is_filled=True).count()
                    section.save()

                    messages.success(request, "Student admitted successfully!")
            except IntegrityError:
                messages.error(request, "The selected seat is already taken by another admission. Please select a different seat.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
            return redirect('schools:admissions')
        else:
            messages.error(request, "Please correct the errors in the admission form.")

    context = {
        'school': school,
        'cycle_classes': cycle_classes,  # Pass cycle-wise data as a list
        'admission_form': admission_form,
        'pending_applications': pending_applications,
    }
    return render(request, 'schools/admissions.html', context)




from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import SchoolProfile, Admission, SchoolClass, ClassSection, Seat, AdmissionCycle
from django.db import IntegrityError
from core.signals import application_status_updated
import logging

logger = logging.getLogger(__name__)

@login_required
def applications(request):
    if request.user.user_type != 'school':
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    try:
        school = SchoolProfile.objects.get(user=request.user)
        # Get all applications for this school with cycle info
        applications = Admission.objects.filter(school=school).select_related('school_class__cycle')

        # Get search parameters
        admission_id = request.GET.get('admission_id', '').strip()
        student_name = request.GET.get('student_name', '').strip()
        class_id = request.GET.get('class_id', '').strip()
        section_id = request.GET.get('section_id', '').strip()
        cycle_id = request.GET.get('cycle_id', '').strip()

        # Apply search filters
        if admission_id:
            applications = applications.filter(admission_id__icontains=admission_id)
            logger.info(f"Filtered by admission_id: {admission_id}")
        
        if student_name:
            applications = applications.filter(
                Q(student__username__icontains=student_name) |
                Q(student__student_profile__first_name__icontains=student_name) |
                Q(student__student_profile__last_name__icontains=student_name)
            )
            logger.info(f"Filtered by student_name: {student_name}")
        
        if class_id:
            applications = applications.filter(school_class__id=class_id)
            logger.info(f"Filtered by class_id: {class_id}")
        
        if section_id:
            applications = applications.filter(section__id=section_id)
            logger.info(f"Filtered by section_id: {section_id}")
        
        if cycle_id:
            applications = applications.filter(school_class__cycle__id=cycle_id)
            logger.info(f"Filtered by cycle_id: {cycle_id}")

        # Get all cycles (even empty ones)
        cycles = AdmissionCycle.objects.filter(school=school).order_by('-year')
        cycle_applications = {}
        for cycle in cycles:
            cycle_apps = applications.filter(school_class__cycle=cycle)
            if cycle_apps.exists() or not cycle_id:
                cycle_applications[cycle] = {
                    'pending': cycle_apps.filter(status='Pending'),
                    'approved': cycle_apps.filter(status='Approved'),
                    'rejected': cycle_apps.filter(status='Rejected'),
                }

        # Get unique classes and sections based on selected cycle or all if no cycle filter
        classes = SchoolClass.objects.filter(school=school).distinct()
        if cycle_id:
            classes = classes.filter(cycle__id=cycle_id)
        sections = ClassSection.objects.filter(school_class__school=school).distinct()
        if cycle_id:
            sections = sections.filter(school_class__cycle__id=cycle_id)
        elif class_id:
            sections = sections.filter(school_class__id=class_id)
        logger.info(f"Fetched cycles: {cycles.count()}, classes: {classes.count()}, sections: {sections.count()}")

    except SchoolProfile.DoesNotExist:
        school = None
        cycle_applications = {}
        cycles = []
        classes = []
        sections = []
        logger.error("SchoolProfile not found for user: %s", request.user.username)

    if request.method == 'POST' and 'approve_application' in request.POST:
        if school is None:
            messages.error(request, "Please set up your school profile to approve applications.")
            return redirect('schools:applications')
        application_id = request.POST.get('application_id')
        seat_id = request.POST.get('seat_id')
        auto_assign = request.POST.get('auto_assign') == 'true'
        class_id = request.POST.get('class_id')
        section_id = request.POST.get('section_id')

        application = get_object_or_404(Admission, id=application_id, school=school, status='Pending')
        section = get_object_or_404(ClassSection, id=section_id, school_class__id=class_id)
        school_class = get_object_or_404(SchoolClass, id=class_id, school=school)

        if not application.student:
            messages.error(request, "This application has no student assigned.")
            logger.error(f"No student assigned for application_id: {application_id}")
            return redirect('schools:applications')

        # Auto assign seat if selected, else use manual selection
        if auto_assign:
            available_seats = Seat.objects.filter(section=section, is_filled=False)
            if available_seats.exists():
                seat = available_seats.first()
                logger.info(f"Auto-assigned seat {seat.seat_number} for application_id: {application_id}")
            else:
                messages.error(request, "No available seats for auto-assignment.")
                logger.error(f"No available seats for application_id: {application_id}")
                return redirect('schools:applications')
        else:
            if not seat_id:
                messages.error(request, "Please select a seat for the student.")
                logger.warning(f"No seat selected for application_id: {application_id}")
                return redirect('schools:applications')
            seat = get_object_or_404(Seat, id=seat_id, section__id=section_id)

        if seat.section != section or seat.section.school_class != school_class:
            messages.error(request, "The selected seat does not belong to the selected class or section.")
            logger.error(f"Seat mismatch for application_id: {application_id}, seat_id: {seat_id}")
            return redirect('schools:applications')

        if not seat.is_filled:
            try:
                if application.seat and application.seat != seat:
                    old_seat = application.seat
                    old_seat.is_filled = False
                    old_seat.student = None
                    old_seat.save()
                    # old_section = old_seat.section
                    # old_section.filled_seats = max(0, old_section.filled_seats - 1)
                    # old_section.save()  # Commented out due to missing field
                    logger.info(f"Cleared old seat {old_seat.seat_number} for application_id: {application_id}")

                application.seat = seat
                application.school_class = school_class
                application.section = section
                application.status = 'Approved'
                application.save()

                seat.is_filled = True
                seat.student = application.student
                seat.save()

                # section.filled_seats += 1  # Commented out due to missing field
                # section.save()  # Commented out due to missing field

                application_status_updated.send(
                    sender=None,
                    student=application.student,
                    institution=school,
                    application=application
                )

                messages.success(request, "Application approved successfully!")
                logger.info(f"Approved application_id: {application_id}, assigned seat: {seat.seat_number}")
            except IntegrityError:
                messages.error(request, "The selected seat is already taken by another admission. Please select a different seat.")
                logger.error(f"IntegrityError for application_id: {application_id}, seat_id: {seat_id}")
        else:
            messages.error(request, "The selected seat is already taken.")
            logger.error(f"Seat already filled for application_id: {application_id}, seat_id: {seat_id}")
        return redirect('schools:applications')

    if request.method == 'POST' and 'reject_application' in request.POST:
        if school is None:
            messages.error(request, "Please set up your school profile to reject applications.")
            return redirect('schools:applications')
        application_id = request.POST.get('application_id')
        application = get_object_or_404(Admission, id=application_id, school=school, status='Pending')
        seat = application.seat

        application.status = 'Rejected'
        application.seat = None
        application.save()

        if seat:
            seat.is_filled = False
            seat.student = None
            seat.save()
            # section = seat.section
            # section.filled_seats = max(0, section.filled_seats - 1)
            # section.save()  # Commented out due to missing field
            logger.info(f"Rejected application_id: {application_id}, cleared seat: {seat.seat_number}")

        application_status_updated.send(
            sender=None,
            student=application.student,
            institution=school,
            application=application
        )

        messages.success(request, "Application rejected successfully!")
        logger.info(f"Rejected application_id: {application_id}")
        return redirect('schools:applications')

    context = {
        'school': school,
        'cycle_applications': cycle_applications,
        'cycles': cycles,
        'classes': classes,
        'sections': sections,
        'cycle_id': cycle_id,
    }
    return render(request, 'schools/applications.html', context)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Q
from schools.models import Admission, SchoolProfile, SchoolClass, ClassSection, Seat, AdmissionCycle
import logging

logger = logging.getLogger(__name__)

@login_required
def view_application_details(request, application_id):
    if request.user.user_type != 'school':
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    try:
        school = SchoolProfile.objects.get(user=request.user)
        admission = get_object_or_404(Admission, id=application_id, school=school)
        logger.info("Fetched admission %s for school %s", admission.id, school.school_name)
        
        context = {
            'admission': admission,
            'school': school,
            'app_type': 'School',
        }
        return render(request, 'schools/view_application_details.html', context)
    except SchoolProfile.DoesNotExist:
        logger.error("SchoolProfile not found for user: %s", request.user.username)
        messages.error(request, "Please set up your school profile to view applications.")
        return redirect('schools:applications')


from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .models import SchoolProfile, SchoolClass, ClassSection, Seat, Admission
from .forms import AdmissionForm
from django.contrib.auth import get_user_model
from students.models import StudentProfile  # Import the StudentProfile model

@login_required
def student_details(request, student_id):
    if request.user.user_type != 'school':
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # Use the custom user model
    User = get_user_model()
    student = get_object_or_404(User, id=student_id, user_type='student')
    
    # Fetch the student's profile
    student_profile = get_object_or_404(StudentProfile, user=student)
    
    try:
        school = SchoolProfile.objects.get(user=request.user)
        # Fetch the student's applications for this school
        applications = Admission.objects.filter(school=school, student=student)
    except SchoolProfile.DoesNotExist:
        school = None
        applications = []

    context = {
        'school': school,
        'student': student,
        'student_profile': student_profile,  # Add the student profile to the context
        'applications': applications,
    }
    return render(request, 'schools/student_details.html', context)











from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import SchoolProfile, SchoolClass, ClassSection
import logging

logger = logging.getLogger(__name__)

@login_required
def get_sections(request):
    logger.debug(f"get_sections called with class_id: {request.GET.get('class_id')}, school_id: {request.GET.get('school_id')}, cycle_id: {request.GET.get('cycle_id')}")
    
    class_id = request.GET.get('class_id')
    school_id = request.GET.get('school_id')
    cycle_id = request.GET.get('cycle_id')
    
    if not class_id or not school_id or not cycle_id:
        logger.warning(f"Missing parameters: class_id={class_id}, school_id={school_id}, cycle_id={cycle_id}")
        return JsonResponse({'error': 'class_id, school_id, and cycle_id are required'}, status=400)

    try:
        class_id = int(class_id)
        school_id = int(school_id)
        cycle_id = int(cycle_id)
        # Verify the school belongs to the user
        school = SchoolProfile.objects.get(id=school_id, user=request.user)
        school_class = get_object_or_404(SchoolClass, id=class_id, school_id=school_id, cycle_id=cycle_id)
        sections = ClassSection.objects.filter(school_class=school_class, cycle_id=cycle_id).prefetch_related('seats')
        sections_data = [
            {
                'id': section.id,
                'section_name': section.section_name,
                'available_seats': section.total_seats - section.seats.filter(is_filled=True).count()
            } for section in sections
        ]
        logger.info(f"Found {len(sections_data)} sections for class_id={class_id}, cycle_id={cycle_id}")
        return JsonResponse({'sections': sections_data})
    except SchoolProfile.DoesNotExist:
        logger.error(f"School not found or unauthorized: school_id={school_id}")
        return JsonResponse({'error': 'School not found or unauthorized'}, status=403)
    except SchoolClass.DoesNotExist:
        logger.error(f"Class not found: class_id={class_id}, cycle_id={cycle_id}")
        return JsonResponse({'error': 'Class not found'}, status=404)
    except ValueError:
        logger.error(f"Invalid parameters: class_id={class_id}, school_id={school_id}, cycle_id={cycle_id}")
        return JsonResponse({'error': 'Invalid class_id, school_id, or cycle_id'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in get_sections: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)
    



# def get_seats(request, section_id):
#     try:
#         section = get_object_or_404(ClassSection, id=section_id)
#         seats = section.seats.all()
#         seats_data = [{'id': seat.id, 'seat_number': seat.seat_number, 'is_filled': seat.is_filled} for seat in seats]
#         return JsonResponse({'seats': seats_data})
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import SchoolProfile, AdmissionCycle, SchoolClass, ClassSection, Admission
from .forms import StudentApplicationForm
from django.db.models.signals import Signal

# Define signal (assuming it's defined elsewhere; include if not already in your codebase)
application_submitted = Signal()

# schools/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import SchoolProfile, AdmissionCycle, SchoolClass, ClassSection, Admission
from .forms import StudentApplicationForm
from django.db.models.signals import Signal
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Define signal
application_submitted = Signal()

@login_required
def apply_for_admission(request, school_id):
    if request.user.user_type != 'student':
        return HttpResponseForbidden("You are not authorized to access this page.")

    school = get_object_or_404(SchoolProfile, id=school_id)
    cycles = AdmissionCycle.objects.filter(school=school, is_active=True).order_by('-year')
    logger.debug(f"Found {cycles.count()} active cycles for school_id={school_id}: {[c.year for c in cycles]}")

    # Check for active application
    active_application = Admission.objects.filter(
        student=request.user,
        school=school,
        status__in=['Pending', 'Approved']
    ).first()

    if request.method == 'POST':
        logger.debug(f"POST data: {request.POST}")
        if 'submit_application' in request.POST:
            # Full form submission
            form = StudentApplicationForm(request.POST, request.FILES, school_id=school_id)
            if form.is_valid():
                cycle = form.cleaned_data['cycle']
                logger.debug(f"Submitting application for cycle_id={cycle.id}")
                if not cycle.is_active:
                    messages.error(request, "Cannot apply for an inactive cycle.")
                elif active_application:
                    messages.error(request, f"You already have an active application at {school.school_name}. Withdraw it to apply again.")
                else:
                    school_class = form.cleaned_data['school_class']
                    section = form.cleaned_data['section']
                    available_seats = section.available_seats()
                    logger.debug(f"Section {section.section_name} has {available_seats} seats available")

                    if available_seats > 0:
                        admission = form.save(commit=False)
                        admission.school = school
                        admission.cycle = cycle
                        admission.school_class = school_class
                        admission.section = section
                        admission.student = request.user
                        admission.status = 'Pending'
                        admission.save()
                        application_submitted.send(sender=Admission, student=request.user, institution=school, application=admission)
                        messages.success(request, "Application submitted successfully! Awaiting school approval.")
                        return redirect('schools:application_success')
                    else:
                        messages.error(request, "No seats available in this section.")
            else:
                messages.error(request, "Please correct the errors in the form.")
                for field, errors in form.errors.items():
                    logger.error(f"Form error - Field: {field}, Errors: {errors}")
        else:
            # Partial submission for dropdown updates
            form = StudentApplicationForm(
                data=request.POST,
                files=request.FILES,
                school_id=school_id
            )
            # Log form data for debugging
            cycle_id = request.POST.get('cycle')
            class_id = request.POST.get('school_class')
            logger.debug(f"Partial submission: cycle_id={cycle_id}, class_id={class_id}")
            if cycle_id:
                try:
                    cycle_id = int(cycle_id)
                    classes = SchoolClass.objects.filter(school_id=school_id, cycle_id=cycle_id)
                    logger.debug(f"Classes for cycle_id={cycle_id}: {[c.grade for c in classes]}")
                except (ValueError, TypeError):
                    logger.warning(f"Invalid cycle_id: {cycle_id}")
            if class_id and cycle_id:
                try:
                    class_id = int(class_id)
                    cycle_id = int(cycle_id)
                    sections = ClassSection.objects.filter(school_class_id=class_id, cycle_id=cycle_id)
                    logger.debug(f"Sections for class_id={class_id}, cycle_id={cycle_id}: {[s.section_name for s in sections]}")
                except (ValueError, TypeError):
                    logger.warning(f"Invalid class_id or cycle_id: class_id={class_id}, cycle_id={cycle_id}")
    else:
        form = StudentApplicationForm(school_id=school_id)
        logger.debug("GET request: Initial form loaded")

    context = {
        'school': school,
        'cycles': cycles,
        'form': form,
        'active_application': active_application,
    }
    return render(request, 'schools/apply.html', context)


from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from schools.models import SchoolProfile, Admission

@login_required
def school_list(request):
    if request.user.user_type != 'student':
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # Get all schools initially
    schools = SchoolProfile.objects.all()

    # Get filter and search parameters from GET request
    district = request.GET.get('district', '')
    state = request.GET.get('state', '')
    school_type = request.GET.get('school_type', '')
    search_query = request.GET.get('search', '')

    # Apply filters
    if district:
        schools = schools.filter(district__iexact=district)
    if state:
        schools = schools.filter(state__iexact=state)
    if school_type:
        schools = schools.filter(school_type__iexact=school_type)
    if search_query:
        schools = schools.filter(school_name__icontains=search_query)

    # Get distinct values for filters
    districts = SchoolProfile.objects.values_list('district', flat=True).distinct()
    states = SchoolProfile.objects.values_list('state', flat=True).distinct()
    school_types = SchoolProfile.objects.values_list('school_type', flat=True).distinct()

    # Check which schools the student has applied to
    applied_schools = set()
    if request.user.is_authenticated:
        applied_admissions = Admission.objects.filter(student=request.user, status='Pending').values_list('school_id', flat=True)
        applied_schools = set(applied_admissions)

    context = {
        'schools': schools,
        'districts': districts,
        'states': states,
        'school_types': school_types,
        'selected_district': district,
        'selected_state': state,
        'selected_school_type': school_type,
        'search_query': search_query,
        'applied_schools': applied_schools,  # Pass applied schools list
    }
    return render(request, 'schools/school_list.html', context)





from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.db import IntegrityError
from schools.models import SchoolProfile, SchoolClass, Seat, Admission
from .forms import StudentApplicationForm
from core.signals import application_submitted  # Import the signal

@login_required
def school_seats(request, school_id):
    if request.user.user_type != 'student':
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    school = get_object_or_404(SchoolProfile, id=school_id)
    classes = SchoolClass.objects.filter(school=school).prefetch_related('sections__seats')

    # Calculate filled and available seats dynamically
    for school_class in classes:
        for section in school_class.sections.all():
            section.filled_seats_dynamic = section.seats.filter(is_filled=True).count()
            section.available_seats = section.total_seats - section.filled_seats_dynamic

    application_form = StudentApplicationForm(request.POST or None)

    # Fetch all active applications for display (across all schools)
    active_applications = Admission.objects.filter(
        student=request.user,
        status__in=['Pending', 'Approved']
    )

    if request.method == 'POST' and 'apply_with_seat' in request.POST:
        if application_form.is_valid():
            seat_id = request.POST.get('seat_id')
            seat = get_object_or_404(Seat, id=seat_id)
            section = seat.section
            school_class = section.school_class
            school_from_seat = school_class.school

            if school_from_seat != school:
                return HttpResponseForbidden("Invalid seat selection.")

            # Check if the student has an active application for THIS school
            active_application_for_school = Admission.objects.filter(
                student=request.user,
                school=school,
                status__in=['Pending', 'Approved']
            ).first()

            if active_application_for_school:
                error_message = (
                    f"You already have an active application for Class {active_application_for_school.school_class.grade} "
                    f"at {active_application_for_school.school.school_name} (Status: {active_application_for_school.status}). "
                    "You can only apply to one class per school at a time. "
                    f"<a href='/students/application/withdraw/{active_application_for_school.id}/'>Withdraw your current application</a> to apply to a different class in this school."
                )
                application_form.add_error(None, error_message)
            else:
                existing_seat_application = Admission.objects.filter(seat=seat, status__in=['Pending', 'Approved']).exists()
                rejected_seat_application = Admission.objects.filter(seat=seat, status='Rejected').first()
                if rejected_seat_application:
                    rejected_seat_application.seat = None
                    rejected_seat_application.save()

                if existing_seat_application:
                    application_form.add_error(None, "This seat is currently reserved by another pending or approved application. Please select a different seat.")
                elif not seat.is_filled:
                    try:
                        application = application_form.save(commit=False)
                        application.school = school
                        application.school_class = school_class
                        application.section = section
                        application.seat = seat
                        application.student = request.user
                        application.status = 'Pending'
                        application.save()

                        # Do NOT mark the seat as filled yet
                        # seat.is_filled = True  # Removed this line
                        # seat.save()  # Removed this line

                        # Trigger the application submitted signal
                        application_submitted.send(
                            sender=None,
                            student=request.user,
                            school=school.user,
                            application=application
                        )

                        messages.success(request, "Application submitted successfully! Please wait for the school to review your application.")
                        return redirect('schools:application_success')
                    except IntegrityError:
                        application_form.add_error(None, "This seat is currently reserved by another application. Please select a different seat.")
                else:
                    application_form.add_error(None, "The selected seat is already taken.")

    context = {
        'school': school,
        'classes': classes,
        'application_form': application_form,
        'active_applications': active_applications,
    }
    return render(request, 'schools/school_seats.html', context)





def application_success(request):
    return render(request, 'schools/application_success.html')



from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import SchoolProfile, SchoolClass
import logging

logger = logging.getLogger(__name__)

@login_required
def get_classes(request):
    school_id = request.GET.get('school_id')
    cycle_id = request.GET.get('cycle_id')
    
    logger.debug(f"get_classes called with school_id={school_id}, cycle_id={cycle_id}")
    
    if not school_id or not cycle_id:
        logger.warning(f"Missing parameters: school_id={school_id}, cycle_id={cycle_id}")
        return JsonResponse({'error': 'school_id and cycle_id are required'}, status=400)
    
    try:
        school_id = int(school_id)
        cycle_id = int(cycle_id)
        # Verify school ownership
        school = SchoolProfile.objects.get(id=school_id, user=request.user)
        classes = SchoolClass.objects.filter(school_id=school_id, cycle_id=cycle_id).values('id', 'grade')
        logger.info(f"Found {classes.count()} classes for school_id={school_id}, cycle_id={cycle_id}: {[cls['grade'] for cls in classes]}")
        if classes.count() == 0:
            logger.warning(f"No classes found for school_id={school_id}, cycle_id={cycle_id}")
        return JsonResponse({'classes': list(classes)})
    except SchoolProfile.DoesNotExist:
        logger.error(f"School not found or unauthorized: school_id={school_id}")
        return JsonResponse({'error': 'School not found or unauthorized'}, status=403)
    except ValueError:
        logger.error(f"Invalid parameters: school_id={school_id}, cycle_id={cycle_id}")
        return JsonResponse({'error': 'Invalid school_id or cycle_id'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in get_classes: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)





from django.http import JsonResponse
from django.shortcuts import get_object_or_404

# @login_required
# def get_seats(request):
#     section_id = request.GET.get('section_id')
    

#     if not section_id:
#         return JsonResponse({'seats': []}, status=400)
    
#     try:
#         section_id = int(section_id)
#     except ValueError:
#         return JsonResponse({'seats': []}, status=400)

   
#     school = get_object_or_404(SchoolProfile, user=request.user)
#     section = get_object_or_404(ClassSection, id=section_id, school_class__school=school)
    

#     seats = Seat.objects.filter(section=section).values('id', 'seat_number', 'is_filled')
#     return JsonResponse({'seats': list(seats)})


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError, IntegrityError, connection
from .models import SchoolProfile, ClassSection, Seat
import logging
import traceback

# Set up logging
logger = logging.getLogger(__name__)

@login_required
def get_seats(request, section_id):
    logger.debug(f"get_seats called with section_id: {section_id}, user: {request.user.username if request.user.is_authenticated else 'Anonymous'}")
    try:
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            logger.error("User is not authenticated")
            return JsonResponse({'error': 'User is not authenticated'}, status=401)

        # Check if the request is AJAX
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            logger.error("Request is not an AJAX request")
            return JsonResponse({'error': 'This endpoint only supports AJAX requests'}, status=400)

        # Validate section_id
        try:
            section_id = int(section_id)
        except (ValueError, TypeError):
            logger.error(f"Invalid section_id: {section_id}")
            return JsonResponse({'error': 'Invalid section_id: must be an integer'}, status=400)

        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            logger.debug("Database connection is working")
        except DatabaseError as e:
            logger.error(f"Database connection error: {str(e)}", exc_info=True)
            return JsonResponse({'error': f'Database connection error: {str(e)}'}, status=500)

        # Check user permissions
        if not request.user.is_active:
            logger.error(f"User {request.user.username} is not active")
            return JsonResponse({'error': 'User account is not active'}, status=403)

        # Get the school profile for the current user
        logger.debug(f"Fetching SchoolProfile for user: {request.user.username}")
        school = get_object_or_404(SchoolProfile, user=request.user)
        logger.debug(f"SchoolProfile found: {school}")

        # Ensure the section belongs to the current school
        logger.debug(f"Fetching ClassSection with id: {section_id} for school: {school}")
        section = get_object_or_404(ClassSection, id=section_id, school_class__school=school)
        logger.debug(f"ClassSection found: {section}")

        # Fetch seats for the section
        logger.debug(f"Fetching seats for ClassSection: {section}")
        try:
            seats = Seat.objects.filter(section=section).values('id', 'seat_number', 'is_filled')
            seats_list = list(seats)  # Force evaluation to catch any query errors
            logger.debug(f"Seats found: {seats_list}")
        except Exception as e:
            logger.error(f"Error fetching seats for ClassSection {section}: {str(e)}", exc_info=True)
            seats_list = []
            logger.debug("Falling back to empty seats list")

        logger.debug(f"Seats data prepared: {seats_list}")
        return JsonResponse({'seats': seats_list})

    except ClassSection.DoesNotExist:
        logger.error(f"ClassSection with id {section_id} not found for school: {school}")
        return JsonResponse({'error': 'Section not found'}, status=404)
    except DatabaseError as e:
        logger.error(f"Database error in get_seats for section_id {section_id}: {str(e)}", exc_info=True)
        return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)
    except IntegrityError as e:
        logger.error(f"Integrity error in get_seats for section_id {section_id}: {str(e)}", exc_info=True)
        return JsonResponse({'error': f'Database integrity error: {str(e)}'}, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in get_seats for section_id {section_id}: {str(e)}\n{traceback.format_exc()}", exc_info=True)
        return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)
    



# schools/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import SchoolProfile, AdmissionCycle
from .forms import AdmissionCycleForm  # Ensure this form exists

@login_required
def create_cycle(request):
    if request.user.user_type != 'school':  # Assuming user_type is in your User model
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    try:
        school = SchoolProfile.objects.get(user=request.user)
    except SchoolProfile.DoesNotExist:
        messages.error(request, "Please set up your school profile first.")
        return redirect('schools:school_profile')

    if request.method == 'POST':
        form = AdmissionCycleForm(request.POST, school=school)  # Pass school to form
        if form.is_valid():
            cycle = form.save(commit=False)
            cycle.school = school  # Explicitly set school (redundant but safe)
            cycle.save()
            messages.success(request, f"Admission cycle {cycle.year} created successfully!")
            return redirect('schools:cycle_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AdmissionCycleForm(school=school)  # Pass school to form

    context = {
        'school': school,
        'form': form,
    }
    return render(request, 'schools/create_cycle.html', context)

@login_required
def edit_cycle(request, cycle_id):
    if request.user.user_type != 'school':
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    cycle = get_object_or_404(AdmissionCycle, id=cycle_id, school__user=request.user)
    if request.method == 'POST':
        form = AdmissionCycleForm(request.POST, instance=cycle, school=cycle.school)  # Pass existing school
        if form.is_valid():
            form.save()
            messages.success(request, f"Admission cycle {cycle.year} updated successfully!")
            return redirect('schools:cycle_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AdmissionCycleForm(instance=cycle, school=cycle.school)

    context = {
        'school': cycle.school,
        'form': form,
        'cycle': cycle,
    }
    return render(request, 'schools/edit_cycle.html', context)

@login_required
def cycle_list(request):
    if request.user.user_type != 'school':
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    try:
        school = SchoolProfile.objects.get(user=request.user)
        cycles = AdmissionCycle.objects.filter(school=school).order_by('-year')
    except SchoolProfile.DoesNotExist:
        messages.error(request, "Please set up your school profile first.")
        return redirect('schools:school_profile')

    context = {
        'school': school,
        'cycles': cycles,
    }
    return render(request, 'schools/cycle_list.html', context)



from django.shortcuts import render
from .models import SchoolProfile

def packages(request):
    # Get institution type if available (for now, assume school; extend for colleges later)
    institution_type = 'school'  # Default
    if request.user.is_authenticated and hasattr(request.user, 'school_profile'):
        try:
            school_profile = SchoolProfile.objects.get(user=request.user)
            institution_type = school_profile.school_type.lower() if school_profile.school_type else 'school'
        except SchoolProfile.DoesNotExist:
            pass

    context = {
        'institution_type': institution_type,
        'digital_marketing_packages': [
            {
                'name': 'Basic Package',
                'price': '₹9,999/month',
                'features': [
                    '5 Social Media Posts (Facebook, Instagram)',
                    '1 Promotional Video',
                    'Basic SEO for School Website',
                    'Google My Business Optimization',
                    'Lead Generation Form Setup',
                ],
            },
            {
                'name': 'Standard Package',
                'price': '₹19,999/month',
                'features': [
                    '10 Social Media Posts (FB, Insta, LinkedIn)',
                    '2 Promotional Videos + Reels',
                    'Advanced SEO & Website Optimization',
                    'Facebook & Instagram Ads (₹3,000 Ad Budget Included)',
                    'Google My Business & Reviews Management',
                    'Lead Generation Campaigns',
                ],
            },
            {
                'name': 'Premium Package',
                'price': '₹29,999/month',
                'features': [
                    '15 Social Media Posts (FB, Insta, LinkedIn, Twitter)',
                    '3 Promotional Videos + Reels',
                    'Full SEO + Blog Writing (2 Blogs/Month)',
                    'Paid Ad Campaigns on FB, Insta (₹5,000 Ad Budget Included)',
                    'School Admission Landing Page',
                    'Google My Business & Reviews Management',
                ],
            },
        ],
        'academia_package': {
            'name': 'Academia Admission Package',
            'price': '₹TBD/month',  # Placeholder, update later
            'features': [
                'Online Application Form',
                'Student Data Management',
                'Institution Listing & Filtering',
                '2000 Applications/Month',
                'Email Notifications',
                'Institution Data Analytics',
                'Admin Seat Visualization',
                'Institution Landing Page',
                'Payment Gateway Integration',
            ],
        },
    }
    return render(request, 'schools/packages.html', context)