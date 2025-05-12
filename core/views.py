from django.shortcuts import render, redirect
from django.contrib import messages


def register_options(request):
    return render(request, 'core/register_options.html')

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

# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.db import IntegrityError
# from .forms import RegistrationForm
# from core.signals import user_registered

# def register(request):
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             try:
#                 user = form.save()
#                 messages.success(request, 'Registration successful! Awaiting admin approval.')
#                 user_registered.send(sender=None, user=user)
#                 return redirect('core:login')
#             except IntegrityError:
#                 messages.error(request, 'Username or email already exists. Please choose a different one.')
#         else:
#             messages.error(request, 'Please correct the errors below.')
#     else:
#         form = RegistrationForm()
#     return render(request, 'core/register.html', {'form': form})


from django.shortcuts import render
from schools.models import SchoolProfile
from colleges.models import CollegeProfile

def home(request):
    # Define the selected cities
    selected_cities = ['Hyderabad', 'Vijayawada', 'Visakhapatnam', 'Avanigadda']

    # Get the selected city from the query parameter, default to Hyderabad
    selected_city = request.GET.get('city', selected_cities[0])

    # Ensure the selected city is valid (case-insensitive comparison)
    selected_city = next((city for city in selected_cities if city.lower() == selected_city.lower()), selected_cities[0])

    # Fetch approved school and college profiles for all selected cities
    all_school_profiles = {}
    all_college_profiles = {}

    for city in selected_cities:
        # Fetch all approved schools for the city to get the total count
        all_schools = SchoolProfile.objects.filter(
            user__is_approved=True, 
            city__iexact=city
        )
        # Store the total count and the 8 most recent schools
        all_school_profiles[city] = {
            'schools': all_schools.order_by('-id')[:4],  # 8 most recent schools
            'total_count': all_schools.count()  # Total number of schools
        }

        # Fetch all approved colleges for the city to get the total count
        all_colleges = CollegeProfile.objects.filter(
            user__is_approved=True, 
            city__iexact=city
        )
        # Store the total count and the 8 most recent colleges
        all_college_profiles[city] = {
            'colleges': all_colleges.order_by('-id')[:4],  # 8 most recent colleges
            'total_count': all_colleges.count()  # Total number of colleges
        }

    context = {
        'selected_cities': selected_cities,
        'selected_city': selected_city,
        'all_school_profiles': all_school_profiles,
        'all_college_profiles': all_college_profiles,
    }
    return render(request, 'core/home.html', context)



from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from schools.models import SchoolProfile
from colleges.models import CollegeProfile

def view_all_schools(request):
    # Get filter parameters from the request
    institution_type = request.GET.get('institution_type', 'School')  # Default to School
    state = request.GET.get('state', '')
    district = request.GET.get('district', '')
    city = request.GET.get('city', '')
    page_number = request.GET.get('page', 1)

    # Base queryset based on institution type
    if institution_type == 'College':
        queryset = CollegeProfile.objects.filter(user__is_approved=True)
    else:
        queryset = SchoolProfile.objects.filter(user__is_approved=True)

    # Apply filters dynamically
    if state:
        queryset = queryset.filter(state__iexact=state)
    if district:
        queryset = queryset.filter(district__iexact=district)
    if city:
        queryset = queryset.filter(city__iexact=city)

    # Order by newest first
    queryset = queryset.order_by('-id')

    # Pagination: 10 items per page
    paginator = Paginator(queryset, 10)
    page_obj = paginator.get_page(page_number)

    # Get distinct values for filters
    states = SchoolProfile.objects.values_list('state', flat=True).distinct()
    districts = SchoolProfile.objects.values_list('district', flat=True).distinct()
    cities = SchoolProfile.objects.values_list('city', flat=True).distinct()

    if institution_type == 'College':
        states = CollegeProfile.objects.values_list('state', flat=True).distinct()
        districts = CollegeProfile.objects.values_list('district', flat=True).distinct()
        cities = CollegeProfile.objects.values_list('city', flat=True).distinct()

    context = {
        'page_obj': page_obj,
        'institution_type': institution_type,
        'states': sorted(states),
        'districts': sorted(districts),
        'cities': sorted(cities),
        'selected_state': state,
        'selected_district': district,
        'selected_city': city,
    }
    return render(request, 'core/view_all_schools.html', context)



from django.shortcuts import render, get_object_or_404
from colleges.models import CollegeProfile, AdmissionCycle as CollegeAdmissionCycle, Degree, Department, Section, Course
from schools.models import SchoolProfile, AdmissionCycle as SchoolAdmissionCycle
import logging
import logging
from django.shortcuts import render, get_object_or_404
from colleges.models import CollegeProfile, AdmissionCycle as CollegeAdmissionCycle, Degree, Department, Section, Course, Seat

logger = logging.getLogger(__name__)

def college_detail(request, id):
    # Fetch the college profile by id
    institution = get_object_or_404(CollegeProfile, id=id)
    logger.info(f"Fetched CollegeProfile: {institution.id} - {institution.college_name}")

    # Fetch all active admission cycles for the college
    active_cycles = CollegeAdmissionCycle.objects.filter(
        college=institution, is_active=True, is_archived=False
    ).order_by('-year')
    logger.info(f"Found {active_cycles.count()} active cycles for college {institution.id}: {list(active_cycles.values('id', 'year'))}")

    # Fetch degrees, departments, sections, and courses for each active cycle
    cycles_data = {}
    total_admissions_left = 0  # Initialize total admissions left
    
    for cycle in active_cycles:
        logger.info(f"Processing cycle: {cycle.year}")
        # Fetch degrees for this cycle
        degrees = Degree.objects.filter(college=institution, cycle=cycle)
        logger.info(f"Found {degrees.count()} degrees for cycle {cycle.year}: {list(degrees.values('id', 'name'))}")

        # Fetch departments, sections, and courses for each degree
        degree_data = {}
        for degree in degrees:
            departments = Department.objects.filter(degree=degree, cycle=cycle)
            dept_data = {}
            for dept in departments:
                sections = Section.objects.filter(department=dept, cycle=cycle)
                courses = Course.objects.filter(department=dept, cycle=cycle)
                
                # Ensure seats are created for each section
                for section in sections:
                    current_seats = section.seats.count()
                    if current_seats < section.total_seats:
                        for i in range(current_seats, section.total_seats):
                            Seat.objects.create(
                                section=section,
                                seat_number=f"{section.section_name} {i+1}",
                                is_filled=False
                            )
                
                # Calculate admissions left for the department
                admissions_left = dept.admissions_left()
                logger.info(f"Department: {dept.name}, Total Seats: {dept.total_seats}, Admissions Left: {admissions_left}")
                
                dept_data[dept] = {
                    'sections': sections,
                    'courses': courses,
                    'admissions_left': admissions_left if admissions_left is not None else 0
                }
                
                # Add to total admissions left
                total_admissions_left += admissions_left if admissions_left is not None else 0
            
            degree_data[degree] = dept_data
        cycles_data[cycle] = degree_data
    
    logger.info(f"Cycles data prepared: {len(cycles_data)} cycles")
    logger.info(f"Total Admissions Left for {institution.college_name}: {total_admissions_left}")

    context = {
        'institution': institution,
        'active_cycles': active_cycles,
        'cycles_data': cycles_data,
        'total_admissions_left': total_admissions_left,
    }
    logger.info(f"Context prepared: {context.keys()}")
    return render(request, 'core/college_detail.html', context)

def school_detail(request, id):
    # Fetch the school profile by id
    institution = get_object_or_404(SchoolProfile, id=id)
    logger.info(f"Fetched SchoolProfile: {institution.id} - {institution.school_name}")

    # Fetch active admission cycles for the school
    active_cycles = SchoolAdmissionCycle.objects.filter(
        school=institution, is_active=True, is_archived=False
    ).order_by('-year')
    logger.info(f"Found {active_cycles.count()} active cycles for school {institution.id}: {list(active_cycles.values('id', 'year'))}")

    # Use the first active cycle for display, or None if no active cycles
    current_cycle = active_cycles.first()
    logger.info(f"Current cycle: {current_cycle.year if current_cycle else 'None'}")

    # Fetch classes and sections for each active cycle
    cycles_data = {}
    total_admissions_left = 0
    for cycle in active_cycles:
        logger.info(f"Processing cycle: {cycle.year}")
        # Fetch classes for this cycle
        classes = SchoolClass.objects.filter(school=institution, cycle=cycle)
        logger.info(f"Found {classes.count()} classes for cycle {cycle.year}: {list(classes.values('id', 'grade'))}")

        # Fetch sections for each class
        class_data = {}
        for school_class in classes:
            sections = ClassSection.objects.filter(school_class=school_class, cycle=cycle)
            section_data = {}
            for section in sections:
                available_seats = section.available_seats()
                section_data[section] = {
                    'available_seats': available_seats
                }
                total_admissions_left += available_seats
            class_data[school_class] = section_data
        cycles_data[cycle] = class_data
    logger.info(f"Cycles data prepared: {len(cycles_data)} cycles")
    logger.info(f"Total admissions left: {total_admissions_left}")

    context = {
        'institution': institution,
        'active_cycles': active_cycles,
        'current_cycle': current_cycle,
        'cycles_data': cycles_data,
        'total_admissions_left': total_admissions_left,
    }
    logger.info(f"Context prepared: {context.keys()}")
    return render(request, 'core/school_detail.html', context)




# def school_detail(request, school_id):
#     school = get_object_or_404(SchoolProfile, id=school_id, user__is_approved=True)
#     return render(request, 'core/school_detail.html', {'school': school})

# def college_detail(request, college_id):
#     college = get_object_or_404(CollegeProfile, id=college_id, user__is_approved=True)
#     return render(request, 'core/college_detail.html', {'college': college})





from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm
from .models import User
from super_admin.models import ActivityLog

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

            if not user.is_active:
                messages.error(request, 'Your account has been deactivated.')
                return render(request, 'core/login.html', {'form': form})

            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                if user.is_approved or user.user_type == 'super_admin':
                    login(request, user)
                    # Log the login action with role
                    ActivityLog.objects.create(user=user, role=user.user_type, action="Logged in")
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
    if request.user.is_authenticated:
        # Log the logout action with role
        ActivityLog.objects.create(user=request.user, role=request.user.user_type, action="Logged out")
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


# def clients(request):
#     return render(request, 'core/clients.html')

def clients(request):
    if request.method == 'POST':
        # form fields
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        organization = request.POST.get('organization')
        institution_type = request.POST.get('type')
        location = request.POST.get('location')
        inquiry = request.POST.get('inquiry')
        services = request.POST.get('services')
        role = request.POST.get('role')
        details = request.POST.get('details')

        subject = 'New Contact Inquiry'
        message = f"""
New Contact Inquiry:

First Name: {first_name}
Last Name: {last_name}
Email: {email}
Mobile: {mobile}
Organization Name: {organization}
Type of Institution: {institution_type}
Location: {location}
Nature of Inquiry: {inquiry}
Admission Services Needed: {services}
Role of Contact: {role}
Institution Details: {details}
        """
        recipient_list = ['saibhogadi999@gmail.com']

        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)
            messages.success(request, "Thank you! Your inquiry has been submitted successfully.")
        except Exception as e:
            messages.error(request, f"Something went wrong while sending email: {e}")
        
        
        return redirect('/#contact')

    return render(request, 'core/clients.html')

# def testimonials(request):
#     return render(request, 'core/testimonials.html')

def testimonials(request):
    if request.method == 'POST':
        # form fields
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        organization = request.POST.get('organization')
        institution_type = request.POST.get('type')
        location = request.POST.get('location')
        inquiry = request.POST.get('inquiry')
        services = request.POST.get('services')
        role = request.POST.get('role')
        details = request.POST.get('details')

        subject = 'New Contact Inquiry'
        message = f"""
New Contact Inquiry:

First Name: {first_name}
Last Name: {last_name}
Email: {email}
Mobile: {mobile}
Organization Name: {organization}
Type of Institution: {institution_type}
Location: {location}
Nature of Inquiry: {inquiry}
Admission Services Needed: {services}
Role of Contact: {role}
Institution Details: {details}
        """
        recipient_list = ['saibhogadi999@gmail.com']

        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)
            messages.success(request, "Thank you! Your inquiry has been submitted successfully.")
        except Exception as e:
            messages.error(request, f"Something went wrong while sending email: {e}")
        
        
        return redirect('/#contact')

    return render(request, 'core/testimonials.html')

# def contact(request):
#     return render(request, 'core/contact.html')


def contact(request):
    if request.method == 'POST':
        # form fields
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        organization = request.POST.get('organization')
        institution_type = request.POST.get('type')
        location = request.POST.get('location')
        inquiry = request.POST.get('inquiry')
        services = request.POST.get('services')
        role = request.POST.get('role')
        details = request.POST.get('details')

        subject = 'New Contact Inquiry'
        message = f"""
New Contact Inquiry:

First Name: {first_name}
Last Name: {last_name}
Email: {email}
Mobile: {mobile}
Organization Name: {organization}
Type of Institution: {institution_type}
Location: {location}
Nature of Inquiry: {inquiry}
Admission Services Needed: {services}
Role of Contact: {role}
Institution Details: {details}
        """
        recipient_list = ['saibhogadi999@gmail.com']

        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)
            messages.success(request, "Thank you! Your inquiry has been submitted successfully.")
        except Exception as e:
            messages.error(request, f"Something went wrong while sending email: {e}")
        
        
        return redirect('/#contact')

    return render(request, 'core/contact.html')



from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import EmailMessage
from .forms import InstitutionSelectionForm, OnlineAdmissionForm
from schools.models import SchoolProfile, AdmissionCycle, SchoolClass, ClassSection
from colleges.models import CollegeProfile
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def online_admission(request):
    if request.method == 'POST':
        form = InstitutionSelectionForm(request.POST)
        if form.is_valid():
            institution_id = form.cleaned_data['institution']
            institution_type = form.cleaned_data['institution_type']
            if institution_id and institution_type:
                if institution_type == 'school' and institution_id.startswith('school_'):
                    school_id = institution_id.replace('school_', '')
                    return redirect('core:admission_form', institution_type='school', institution_id=school_id)
                elif institution_type == 'college' and institution_id.startswith('college_'):
                    college_id = institution_id.replace('college_', '')
                    return redirect('core:admission_form', institution_type='college', institution_id=college_id)
                else:
                    messages.error(request, "Selected institution does not match the institution type.")
            else:
                messages.error(request, "Please select an institution type and institution.")
    else:
        form = InstitutionSelectionForm()
    
    return render(request, 'core/online_admission.html', {'form': form})

def get_districts(request):
    state = request.GET.get('state')
    if not state:
        logger.debug("No state provided in get_districts request")
        return JsonResponse({'districts': []})
    
    # Load JSON file
    json_path = os.path.join(settings.BASE_DIR, 'data/indian_states_districts.json')
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
            logger.debug(f"JSON loaded in get_districts: {data}")
        # JSON is a dictionary where keys are states and values are lists of districts
        if state in data:
            districts = sorted(data[state])
            logger.debug(f"Districts for state '{state}': {districts}")
            return JsonResponse({'districts': districts})
        else:
            logger.warning(f"State '{state}' not found in JSON")
            return JsonResponse({'districts': []})
    except Exception as e:
        logger.error(f"Error loading JSON for districts: {str(e)}")
        return JsonResponse({'districts': []})

def get_institutions(request):
    district = request.GET.get('district')
    institution_type = request.GET.get('institution_type')
    if not district:
        logger.debug("No district provided in get_institutions request")
        return JsonResponse({'institutions': []})
    
    logger.debug(f"Fetching institutions for district '{district}' and type '{institution_type}'")
    
    institutions = []
    if institution_type == 'school':
        schools = SchoolProfile.objects.filter(user__is_approved=True, district__iexact=district)
        logger.debug(f"Found {schools.count()} schools for district '{district}'")
        for school in schools:
            logger.debug(f"School: {school.school_name}, District: {school.district}, Approved: {school.user.is_approved}")
            # Include city, board_affiliation, school_type, area (street_address), and school_code in the name
            area = school.street_address if school.street_address else "Unknown Area"
            display_name = f"{school.school_name} ({school.city}, {school.board_affiliation}, {school.school_type}, Area: {area}, Code: {school.school_code or 'No Code'})"
            institutions.append({
                'id': f'school_{school.id}',
                'name': display_name
            })
    elif institution_type == 'college':
        colleges = CollegeProfile.objects.filter(user__is_approved=True, district__iexact=district)
        logger.debug(f"Found {colleges.count()} colleges for district '{district}'")
        for college in colleges:
            logger.debug(f"College: {college.college_name}, District: {college.district}, Approved: {college.user.is_approved}")
            # Include city, college_type, area (street_address), and college_code in the name
            area = college.street_address if college.street_address else "Unknown Area"
            display_name = f"{college.college_name} ({college.city}, {college.college_type}, Area: {area}, Code: {college.college_code or 'No Code'})"
            institutions.append({
                'id': f'college_{college.id}',
                'name': display_name
            })
    
    logger.debug(f"Returning institutions: {institutions}")
    return JsonResponse({'institutions': institutions})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMessage
from .forms import OnlineAdmissionForm
from schools.models import SchoolProfile
from colleges.models import CollegeProfile
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def admission_form(request, institution_type, institution_id):
    if institution_type == 'school':
        institution = get_object_or_404(SchoolProfile, id=institution_id, user__is_approved=True)
        institution_name = institution.school_name
        institution_code = institution.school_code
    elif institution_type == 'college':
        institution = get_object_or_404(CollegeProfile, id=institution_id, user__is_approved=True)
        institution_name = institution.college_name
        institution_code = institution.college_code
    else:
        messages.error(request, "Invalid institution type.")
        return redirect('core:online_admission')
    
    if request.method == 'POST':
        form = OnlineAdmissionForm(
            request.POST,
            request.FILES,
            institution_type=institution_type
        )
        if form.is_valid():
            print("Form is valid! Processing submission...")  # Debug

            # Prepare email for admin
            admin_subject = f"New Admission Application for {institution_type.title()}: {institution_name}"
            admin_body = f"New admission application received for {institution_type.title()}:\n\n"
            admin_body += "Institution Details:\n"
            admin_body += f"Name: {institution_name}\n"
            admin_body += f"Code: {institution_code if institution_code else 'N/A'}\n"
            admin_body += f"Address: {institution.street_address if institution.street_address else 'N/A'}\n"
            admin_body += f"District: {institution.city if institution.city else 'N/A'}\n"
            admin_body += f"State: {institution.state if institution.state else 'N/A'}\n"
            admin_body += f"Pincode: {institution.pincode if institution.pincode else 'N/A'}\n\n"
            admin_body += "Applicant Details:\n"
            for field, value in form.cleaned_data.items():
                if not field.endswith('_certificate') and not field.endswith('_photo') and not field.endswith('_proof'):
                    admin_body += f"{field.replace('_', ' ').title()}: {value}\n"
            
            admin_email = EmailMessage(
                admin_subject,
                admin_body,
                settings.DEFAULT_FROM_EMAIL,
                ['sainaidu6327@gmail.com'],  # Admin email
            )
            for field in ['marksheet', 'transfer_certificate', 'birth_certificate', 'id_proof', 'caste_certificate', 'passport_photo', 'address_proof', 'income_certificate']:
                if form.cleaned_data[field]:
                    file = form.cleaned_data[field]
                    admin_email.attach(file.name, file.read(), file.content_type)
            
            # Prepare confirmation email for user
            user_subject = f"Application Confirmation - {institution_name}"
            user_body = f"Dear {form.cleaned_data['first_name']} {form.cleaned_data['last_name']},\n\n"
            user_body += f"Thank you for applying to {institution_name}!\n"
            user_body += "We have received your application, and our team will review it shortly. You will hear back from us soon.\n\n"
            user_body += "Best regards,\nAcademia Admit Team"

            user_email = EmailMessage(
                user_subject,
                user_body,
                settings.DEFAULT_FROM_EMAIL,
                [form.cleaned_data['email']],  # User email
            )

            # Send emails and handle errors
            email_errors = []
            try:
                admin_email.send()
                logger.debug(f"Admin email sent to sainaidu6327@gmail.com for application to {institution}")
            except Exception as e:
                logger.error(f"Admin email sending failed: {str(e)}")
                email_errors.append(f"Failed to send email to admin: {str(e)}")

            try:
                user_email.send()
                logger.debug(f"User email sent to {form.cleaned_data['email']} for application to {institution}")
            except Exception as e:
                logger.error(f"User email sending failed: {str(e)}")
                email_errors.append(f"Failed to send email to user: {str(e)}")

            if email_errors:
                messages.warning(request, "Application submitted, but there were issues sending emails: " + "; ".join(email_errors))
            else:
                messages.success(request, "Application submitted successfully! Check your email for confirmation.")

            return redirect('core:online_admission')
        else:
            print("Form is invalid. Errors:", form.errors)  # Debug
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = OnlineAdmissionForm(institution_type=institution_type)
    
    return render(request, 'core/admission_form.html', {
        'form': form,
        'institution': institution,
        'institution_type': institution_type,
    })







from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .forms import CustomPasswordResetForm



User = get_user_model()

from django.utils.timezone import now
from datetime import timedelta

def password_reset_request_view(request):
    if request.method == "POST":
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            user = User.objects.filter(email=email).first()

            if user:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                user.password_reset_requested_at = now()
                user.password_reset_created_at = now()
                user.save(update_fields=['password_reset_requested_at', 'password_reset_created_at'])

                reset_url = request.build_absolute_uri(
                    reverse('core:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )

                # Render the email using an HTML template
                email_body = render_to_string('core/password_reset_email.html', {'reset_url': reset_url,'user': user})

                send_mail(
                    subject="Password Reset Request",
                    message="Click the link to reset your password: " + reset_url,  # Fallback plain text
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=email_body  # Send the HTML version
                )
                
                messages.success(request, "A password reset link has been sent to your email.")
                return redirect('core:password_reset_success')
    else:
        form = CustomPasswordResetForm()

    return render(request, 'core/password_reset_request.html', {'form': form})



from django.utils.timezone import now
from datetime import timedelta
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect

User = get_user_model()

def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        messages.error(request, "Invalid reset link.")
        return redirect('core:password_reset')

    # Check token validity
    if not default_token_generator.check_token(user, token):
        messages.error(request, "This reset link is invalid or expired.")
        return redirect('core:password_reset')

    # Check if token is expired (30-minute limit)
    if not user.password_reset_created_at or now() - user.password_reset_created_at > timedelta(minutes=30):
        messages.error(request, "This reset link has expired. Request a new one.")
        return redirect('core:password_reset')

    if request.method == "POST":
        new_password = request.POST['password']
        user.set_password(new_password)
        user.password_reset_created_at = None  # Clear token time after reset
        user.save()
        messages.success(request, "Your password has been reset successfully.")
        return redirect('core:login')

    return render(request, 'core/password_reset_confirm.html', {'validlink': True})



def password_reset_done_view(request):
    return render(request, 'core/password_reset_success.html')