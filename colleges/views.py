# colleges/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CollegeProfile, Department, Degree, Course
from .forms import CollegeProfileForm, DepartmentForm, DegreeForm, CourseForm

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CollegeProfile
from .forms import CollegeProfileForm
from core.signals import profile_updated
import logging

logger = logging.getLogger(__name__)

@login_required
def college_profile(request):
    try:
        college_profile = request.user.college_profile
        show_form = False
    except CollegeProfile.DoesNotExist:
        college_profile = None
        show_form = True

    if request.method == 'POST':
        form = CollegeProfileForm(request.POST, request.FILES, instance=college_profile)
        if form.is_valid():
            college_profile = form.save(commit=False)
            college_profile.user = request.user
            college_profile.save()
            messages.success(request, "College profile saved successfully!")
            profile_updated.send(sender=CollegeProfile, user=request.user)
            return redirect('colleges:college_profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        if college_profile and 'edit' in request.GET:
            show_form = True
        form = CollegeProfileForm(instance=college_profile)

    return render(request, 'colleges/college_profile.html', {
        'form': form,
        'college_profile': college_profile,
        'show_form': show_form,
    })


# colleges/views.py
import logging

logger = logging.getLogger(__name__)

@login_required
def dashboard(request):
    if not hasattr(request.user, 'college_profile'):
        messages.error(request, "You need to create a college profile first.")
        return redirect('colleges:college_profile')

    if not request.user.is_approved:
        messages.error(request, "Your account is not yet approved by the super admin.")
        return redirect('core:login')

    college_profile = request.user.college_profile
    active_cycle = AdmissionCycle.objects.filter(college=college_profile, is_active=True, is_archived=False).first()
    if not active_cycle:
        messages.warning(request, "No active admission cycle available.")
        total_admitted, pending_applications, total_departments, total_seats, filled_seats, available_seats, chart_data, recent_applications = 0, 0, 0, 0, 0, 0, {'labels': [], 'filled_seats': [], 'available_seats': []}, []
    else:
        total_admitted = Application.objects.filter(department__college=college_profile, status='Approved', cycle=active_cycle).count()
        pending_applications = Application.objects.filter(department__college=college_profile, status='Pending', cycle=active_cycle).count()
        total_departments = Department.objects.filter(college=college_profile, cycle=active_cycle).count()
        sections = Section.objects.filter(department__college=college_profile, cycle=active_cycle).prefetch_related('seats')
        total_seats = sum(section.total_seats for section in sections)
        filled_seats = sum(section.seats.filter(is_filled=True).count() for section in sections)
        available_seats = total_seats - filled_seats
        departments = Department.objects.filter(college=college_profile, cycle=active_cycle).prefetch_related('sections__seats')
        chart_data = {'labels': [], 'filled_seats': [], 'available_seats': []}
        for department in departments:
            dept_filled_seats = sum(section.seats.filter(is_filled=True).count() for section in department.sections.all())
            dept_total_seats = sum(section.total_seats for section in department.sections.all())
            dept_available_seats = dept_total_seats - dept_filled_seats
            chart_data['labels'].append(department.name)
            chart_data['filled_seats'].append(dept_filled_seats)
            chart_data['available_seats'].append(dept_available_seats)
        recent_applications = Application.objects.filter(department__college=college_profile, cycle=active_cycle).order_by('-apply_date')[:5]

    logger.info(f"Chart Data: {chart_data}")
    context = {
        'college_profile': college_profile,
        'total_admitted': total_admitted,
        'pending_applications': pending_applications,
        'total_departments': total_departments,
        'total_seats': total_seats,
        'filled_seats': filled_seats,
        'available_seats': available_seats,
        'chart_data': chart_data,
        'recent_applications': recent_applications,
        'active_cycle': active_cycle,
    }
    return render(request, 'colleges/dashboard.html', context)



@login_required
def edit_degree(request, degree_id):
    if not hasattr(request.user, 'college_profile'):
        messages.error(request, "You need to create a college profile first.")
        return redirect('colleges:college_profile')

    college = request.user.college_profile
    degree = get_object_or_404(Degree, id=degree_id, college=college)
    if request.method == 'POST':
        form = DegreeForm(college=college, data=request.POST, instance=degree)
        if form.is_valid():
            form.save()
            messages.success(request, "Degree updated successfully!")
            return redirect('colleges:dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DegreeForm(college=college, instance=degree)

    return render(request, 'colleges/edit_degree.html', {
        'form': form,
        'degree': degree,
        'college': college,
    })


# colleges/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CollegeProfile, Degree, Department, AdmissionCycle
from .forms import DepartmentForm

@login_required
def link_departments(request, degree_id):
    if not hasattr(request.user, 'college_profile'):
        messages.error(request, "You need to create a college profile first.")
        return redirect('colleges:college_profile')

    college_profile = request.user.college_profile
    degree = get_object_or_404(Degree, id=degree_id, college=college_profile)
    cycle_id = request.GET.get('cycle_id', degree.cycle_id)  # Default to degree's cycle

    if request.method == 'POST':
        form = DepartmentForm(college=college_profile, degree=degree, cycle_id=cycle_id, data=request.POST, request=request)
        if form.is_valid():
            department = form.save(commit=False)
            department.college = college_profile
            department.degree = degree
            department.cycle = form.cleaned_data['cycle']
            try:
                department.save()
                messages.success(request, f"Department '{department.name}' added successfully for {degree.name} in {department.cycle.year} cycle!")
                return redirect('colleges:department_list')
            except IntegrityError:
                messages.error(request, f"Department '{department.name}' already exists for this degree and cycle.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DepartmentForm(college=college_profile, degree=degree, cycle_id=cycle_id, request=request)
    return render(request, 'colleges/link_departments.html', {'form': form, 'degree': degree, 'college': college_profile})


@login_required
def edit_department(request, degree_id, department_id):
    if not hasattr(request.user, 'college_profile'):
        messages.error(request, "You need to create a college profile first.")
        return redirect('colleges:college_profile')

    college = request.user.college_profile
    degree = get_object_or_404(Degree, id=degree_id, college=college)
    department = get_object_or_404(Department, id=department_id, degree=degree, college=college)
    if request.method == 'POST':
        form = DepartmentForm(college=college, degree=degree, data=request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, "Department updated successfully!")
            return redirect('colleges:dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DepartmentForm(college=college, degree=degree, instance=department)

    return render(request, 'colleges/edit_department.html', {
        'form': form,
        'department': department,
        'degree': degree,
        'college': college,
    })






# colleges/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from .models import CollegeProfile, AdmissionCycle, Degree, Department, Section, Seat, Application
from .forms import SectionForm, CourseForm

@login_required
def add_section(request, department_id):
    college_profile = get_object_or_404(CollegeProfile, user=request.user)
    department = get_object_or_404(Department, id=department_id, college=college_profile)
    selected_cycle_id = request.GET.get('cycle_id')
    if not selected_cycle_id:
        messages.error(request, "Please select a cycle first.")
        return redirect('colleges:section_list', department_id=department_id)
    selected_cycle = get_object_or_404(AdmissionCycle, id=selected_cycle_id, college=college_profile)
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            section.department = department
            section.cycle = selected_cycle
            section.save()
            # Create seats immediately after saving
            current_seat_count = section.seats.count()
            if current_seat_count < section.total_seats:
                for _ in range(section.total_seats - current_seat_count):
                    Seat.objects.create(section=section, is_filled=False)
            messages.success(request, f"Section {section.section_name} added successfully for department {department.name}!")
            return redirect(reverse('colleges:section_list', kwargs={'department_id': department_id}) + f'?cycle_id={selected_cycle_id}')
    else:
        form = SectionForm()
    return render(request, 'colleges/add_section.html', {'form': form, 'college_profile': college_profile, 'department': department, 'selected_cycle': selected_cycle})

@login_required
def section_seats(request, college_id, degree_id, department_id):
    if not hasattr(request.user, 'college_profile') or request.user.user_type != 'college' or not request.user.is_approved:
        return HttpResponseForbidden("You are not authorized to access this page.")

    college_profile = get_object_or_404(CollegeProfile, id=college_id, user=request.user)
    degree = get_object_or_404(Degree, id=degree_id, college=college_profile)
    department = get_object_or_404(Department, id=department_id, degree=degree, college=college_profile)

    active_cycles = AdmissionCycle.objects.filter(college=college_profile, is_active=True, is_archived=False).order_by('year')
    if not active_cycles.exists():
        messages.error(request, "No active admission cycles are available for this college.")
        return redirect('colleges:section_list', department_id=department_id)

    selected_cycle_id = request.GET.get('cycle_id')
    selected_cycle = get_object_or_404(AdmissionCycle, id=selected_cycle_id, college=college_profile) if selected_cycle_id else active_cycles.first()

    sections = Section.objects.filter(department=department, cycle=selected_cycle).prefetch_related('seats')
    if not sections:
        messages.error(request, "No sections available for this department in the selected cycle.")
        return redirect('colleges:section_list', department_id=department_id)

    applications = Application.objects.filter(department=department, cycle=selected_cycle, status='Approved').select_related('student__student_profile', 'seat')

    for section in sections:
        section.filled_seats_dynamic = section.seats.filter(is_filled=True).count()
        section.available_seats = section.total_seats - section.filled_seats_dynamic
        # Fallback to ensure seats exist
        current_seat_count = section.seats.count()
        if current_seat_count < section.total_seats:
            for _ in range(section.total_seats - current_seat_count):
                Seat.objects.create(section=section, is_filled=False)

    context = {
        'college_profile': college_profile,
        'degree': degree,
        'department': department,
        'sections': sections,
        'applications': applications,
        'cycle': selected_cycle,
        'active_cycles': active_cycles,
    }
    return render(request, 'colleges/section_seats.html', context)

@login_required
def edit_section(request, department_id, section_id):
    if not hasattr(request.user, 'college_profile'):
        messages.error(request, "You need to create a college profile first.")
        return redirect('colleges:college_profile')

    college_profile = request.user.college_profile
    department = get_object_or_404(Department, id=department_id, college=college_profile)
    section = get_object_or_404(Section, id=section_id, department=department)

    if request.user.user_type != 'college' or not request.user.is_approved:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('colleges:section_list', department_id=department_id)

    selected_cycle_id = request.GET.get('cycle_id')
    selected_cycle = get_object_or_404(AdmissionCycle, id=selected_cycle_id, college=college_profile) if selected_cycle_id else section.cycle

    if request.method == 'POST':
        form = SectionForm(data=request.POST, instance=section)
        if form.is_valid():
            old_seats = section.total_seats
            section = form.save()
            new_seats = section.total_seats
            current_seat_count = section.seats.count()
            if new_seats > current_seat_count:
                for _ in range(new_seats - current_seat_count):
                    Seat.objects.create(section=section, is_filled=False)
            elif new_seats < current_seat_count:
                excess_seats = section.seats.filter(is_filled=False).order_by('-id')[:current_seat_count - new_seats]
                for seat in excess_seats:
                    seat.delete()
            messages.success(request, f"Section {section.section_name} updated successfully.")
            return redirect(reverse('colleges:section_seats', args=[college_profile.id, department.degree.id, department.id]) + f'?cycle_id={selected_cycle.id}')
    else:
        form = SectionForm(instance=section)

    return render(request, 'colleges/edit_section.html', {
        'college_profile': college_profile,
        'department': department,
        'section': section,
        'form': form,
        'selected_cycle': selected_cycle,
    })


# colleges/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CollegeProfile, Department, Section

# colleges/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CollegeProfile, Department, Section

@login_required
def delete_section(request, department_id, section_id):
    if not hasattr(request.user, 'college_profile'):
        messages.error(request, "You need to create a college profile first.")
        return redirect('colleges:college_profile')

    college_profile = request.user.college_profile
    department = get_object_or_404(Department, id=department_id, college=college_profile)
    section = get_object_or_404(Section, id=section_id, department=department)

    if request.user.user_type != 'college' or not request.user.is_approved:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('colleges:section_list', department_id=department_id)

    if request.method == 'POST':
        section_name = section.section_name  # Capture name before deletion
        section.delete()
        messages.success(request, f"Section {section_name} deleted successfully.")
        selected_cycle_id = request.GET.get('cycle_id')
        redirect_url = reverse('colleges:section_list', kwargs={'department_id': department_id})
        if selected_cycle_id:
            redirect_url += f'?cycle_id={selected_cycle_id}'
        return redirect(redirect_url)
    return redirect('colleges:section_list', department_id=department_id)  # Redirect if not POST (shouldn't happen with inline form)






@login_required
def edit_course(request, degree_id, department_id, course_id):
    if not hasattr(request.user, 'college_profile'):
        messages.error(request, "You need to create a college profile first.")
        return redirect('colleges:college_profile')

    college = request.user.college_profile
    degree = get_object_or_404(Degree, id=degree_id, college=college)
    department = get_object_or_404(Department, id=department_id, degree=degree, college=college)
    course = get_object_or_404(Course, id=course_id, degree=degree, department=department)
    if request.method == 'POST':
        form = CourseForm(college=college, degree=degree, department=department, data=request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully!")
            return redirect('colleges:course_list', degree_id=degree.id, department_id=department.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CourseForm(college=college, degree=degree, department=department, instance=course)

    return render(request, 'colleges/edit_course.html', {
        'form': form,
        'course': course,
        'degree': degree,
        'department': department,
        'college': college,
    })



@login_required
def course_list(request, degree_id, department_id):
    if not hasattr(request.user, 'college_profile'):
        messages.error(request, "You need to create a college profile first.")
        return redirect('colleges:college_profile')

    college = request.user.college_profile
    degree = get_object_or_404(Degree, id=degree_id, college=college)
    department = get_object_or_404(Department, id=department_id, degree=degree, college=college)
    active_cycle = AdmissionCycle.objects.filter(college=college, is_active=True, is_archived=False).first()
    courses = department.courses.filter(cycle=active_cycle) if active_cycle else []
    return render(request, 'colleges/course_list_all.html', {
        'college': college,
        'degree': degree,
        'department': department,
        'courses': courses,
        'active_cycle': active_cycle,
    })






# colleges/views.py







@login_required
def section_seats(request, college_id, degree_id, department_id):
    if not hasattr(request.user, 'college_profile') or request.user.user_type != 'college' or not request.user.is_approved:
        return HttpResponseForbidden("You are not authorized to access this page.")

    college_profile = get_object_or_404(CollegeProfile, id=college_id, user=request.user)
    degree = get_object_or_404(Degree, id=degree_id, college=college_profile)
    department = get_object_or_404(Department, id=department_id, degree=degree, college=college_profile)

    active_cycles = AdmissionCycle.objects.filter(college=college_profile, is_active=True, is_archived=False).order_by('year')
    if not active_cycles.exists():
        messages.error(request, "No active admission cycles are available for this college.")
        return redirect('colleges:section_list', department_id=department_id)

    selected_cycle_id = request.GET.get('cycle_id')
    selected_cycle = get_object_or_404(AdmissionCycle, id=selected_cycle_id, college=college_profile) if selected_cycle_id else active_cycles.first()

    sections = Section.objects.filter(department=department, cycle=selected_cycle).prefetch_related('seats')
    if not sections:
        messages.error(request, "No sections available for this department in the selected cycle.")
        return redirect('colleges:section_list', department_id=department_id)

    applications = Application.objects.filter(department=department, cycle=selected_cycle, status='Approved').select_related('student__student_profile', 'seat')

    for section in sections:
        section.filled_seats_dynamic = section.seats.filter(is_filled=True).count()
        section.available_seats = section.total_seats - section.filled_seats_dynamic
        # Ensure seats are created if missing (redundant with add_section, but as a fallback)
        current_seat_count = section.seats.count()
        if current_seat_count < section.total_seats:
            for _ in range(section.total_seats - current_seat_count):
                Seat.objects.create(section=section, is_filled=False)

    context = {
        'college_profile': college_profile,
        'degree': degree,
        'department': department,
        'sections': sections,
        'applications': applications,
        'cycle': selected_cycle,
        'active_cycles': active_cycles,
    }
    return render(request, 'colleges/section_seats.html', context)



from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import AdmissionCycle
from colleges.models import CollegeProfile, Application, Section, Seat
from core.signals import application_status_updated, application_submitted
import logging

logger = logging.getLogger(__name__)

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import AdmissionCycle
from colleges.models import CollegeProfile, Application, Section, Seat
from core.signals import application_status_updated, application_submitted
import logging

logger = logging.getLogger(__name__)

@login_required
def manage_applications(request, college_id):
    if not hasattr(request.user, 'college_profile') or request.user.user_type != 'college' or not request.user.is_approved:
        return HttpResponseForbidden("You are not authorized to access this page.")

    college = get_object_or_404(CollegeProfile, id=college_id, user=request.user)
    active_cycles = AdmissionCycle.objects.filter(college=college, is_active=True, is_archived=False).order_by('year')
    if not active_cycles.exists():
        messages.error(request, "No active admission cycles are available for this college.")
        return redirect('colleges:dashboard')

    # Fetch all applications grouped by cycle, include all cycles
    cycle_applications = {}
    for cycle in active_cycles:
        applications = Application.objects.filter(department__college=college, cycle=cycle).select_related('student', 'department', 'section', 'seat', 'student__student_profile')
        pending = applications.filter(status='Pending')
        approved = applications.filter(status='Approved')
        rejected = applications.filter(status='Rejected')
        cycle_applications[cycle] = {
            'pending': pending,
            'approved': approved,
            'rejected': rejected
        }

    sections = {}
    for apps in cycle_applications.values():
        for app in (apps['pending'] | apps['approved'] | apps['rejected']):
            if app.section:
                sections[app.section.id] = app.section
    for section in sections.values():
        section.filled_seats = section.seats.filter(is_filled=True).count()
        section.available_seats = section.total_seats - section.filled_seats

    if request.method == 'POST':
        response = {'success': False, 'message': 'Invalid request.'}
        application_id = request.POST.get('application_id')
        action = request.POST.get('action')
        seat_id = request.POST.get('seat_id')

        if application_id and action in ['approve', 'reject', 'get_student_details']:
            application = get_object_or_404(Application, id=application_id, department__college=college)
            cycle = application.cycle
            old_status = application.status
            if action == 'approve':
                if application.status == 'Approved':
                    response = {'success': False, 'message': f"Application from {application.student.username if application.student else 'Unknown'} is already approved."}
                else:
                    section = application.section
                    if not section:
                        response = {'success': False, 'message': "Section not assigned to application."}
                    else:
                        section.filled_seats = section.seats.filter(is_filled=True).count()
                        section.available_seats = section.total_seats - section.filled_seats

                        if section.available_seats > 0:
                            if seat_id:
                                seat = get_object_or_404(Seat, id=seat_id, section=section, is_filled=False)
                            else:
                                seat = section.seats.filter(is_filled=False).first()
                            if seat:
                                seat.is_filled = True
                                seat.save()
                                application.seat = seat
                                application.status = 'Approved'
                                application.save()
                                response = {
                                    'success': True,
                                    'message': f"Application from {application.student.username if application.student else 'Unknown'} approved and seat {seat.seat_number} assigned.",
                                    'status': 'Approved',
                                    'seat_number': seat.seat_number
                                }
                                if old_status != application.status:
                                    application_status_updated.send(sender=Application, student=application.student, institution=college, application=application)
                            else:
                                response = {'success': False, 'message': "No available seats to assign."}
                        else:
                            response = {'success': False, 'message': "No available seats in the selected section."}
            elif action == 'reject':
                if application.status == 'Rejected':
                    response = {'success': False, 'message': f"Application from {application.student.username if application.student else 'Unknown'} is already rejected."}
                else:
                    if application.seat:
                        application.seat.is_filled = False
                        application.seat.save()
                    application.status = 'Rejected'
                    application.save()
                    response = {
                        'success': True,
                        'message': f"Application from {application.student.username if application.student else 'Unknown'} rejected.",
                        'status': 'Rejected',
                        'seat_number': None
                    }
                    if old_status != application.status:
                        application_status_updated.send(sender=Application, student=application.student, institution=college, application=application)
            elif action == 'get_student_details':
                student = application.student
                profile = student.student_profile if student and hasattr(student, 'student_profile') else None
                response = {
                    'success': True,
                    'student': {
                        'full_name': f"{profile.first_name} {profile.last_name}".strip() if profile else student.username if student else "Unknown",
                        'username': student.username if student else "N/A",
                        'email': student.email if student else "N/A",
                    }
                }

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(response)
        else:
            if response['success']:
                messages.success(request, response['message'])
            else:
                messages.error(request, response['message'])

    context = {
        'college': college,
        'cycle_applications': cycle_applications,
        'sections': sections,
        'active_cycles': active_cycles,
    }
    return render(request, 'colleges/manage_applications.html', context)


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import CollegeProfile, Application
from students.models import StudentProfile  # Import StudentProfile
from django.contrib.auth import get_user_model

@login_required
def college_student_details(request, college_id, student_id):
    if request.user.user_type != 'college':
        return HttpResponseForbidden("You are not authorized to access this page.")

    # Get the college and ensure the logged-in user owns it
    college = get_object_or_404(CollegeProfile, id=college_id, user=request.user)
    
    # Use the custom user model
    User = get_user_model()
    student = get_object_or_404(User, id=student_id, user_type='student')
    
    # Fetch the student's profile
    student_profile = get_object_or_404(StudentProfile, user=student)
    
    # Fetch the student's applications for this college
    applications = Application.objects.filter(department__college=college, student=student)

    context = {
        'college': college,
        'student': student,
        'student_profile': student_profile,
        'applications': applications,
    }
    return render(request, 'colleges/college_student_details.html', context)



# colleges/views.py
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from core.signals import password_changed  # Ensure this signal is defined

@login_required
def college_change_password(request):
    if request.user.user_type != 'college':
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
            return redirect('colleges:dashboard')  # Redirect to college dashboard
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(user=request.user)

    context = {
        'form': form,
    }
    return render(request, 'colleges/change_password.html', context)






from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Degree
import logging

logger = logging.getLogger(__name__)

@login_required
def get_degrees(request):
    cycle_id = request.GET.get('cycle_id')
    logger.debug(f"get_degrees called with cycle_id: {cycle_id}")
    if cycle_id:
        degrees = Degree.objects.filter(cycle_id=cycle_id).values('id', 'name')
        logger.debug(f"Found degrees for cycle {cycle_id}: {list(degrees)}")
        return JsonResponse({'degrees': list(degrees)})
    logger.debug("No valid cycle_id provided")
    return JsonResponse({'degrees': []})

# colleges/views.py
from django.http import JsonResponse
from .models import Department
import logging

logger = logging.getLogger(__name__)
@login_required
def get_departments(request):
    degree_id = request.GET.get('degree_id')
    cycle_id = request.GET.get('cycle_id')
    logger.debug(f"get_departments called with degree_id: {degree_id}, cycle_id: {cycle_id}")
    if degree_id and cycle_id:
        departments = Department.objects.filter(degree_id=degree_id, cycle_id=cycle_id).values('id', 'name')
        logger.debug(f"Found departments: {list(departments)}")
        return JsonResponse({'departments': list(departments)})
    logger.debug("No valid degree_id or cycle_id provided")
    return JsonResponse({'departments': []})


from django.http import JsonResponse
from .models import Section
import logging

logger = logging.getLogger(__name__)
@login_required
def get_sections(request):
    department_id = request.GET.get('department_id')
    cycle_id = request.GET.get('cycle_id')
    logger.debug(f"get_sections called with department_id: {department_id}, cycle_id: {cycle_id}")
    if department_id and cycle_id:
        sections = Section.objects.filter(department_id=department_id, cycle_id=cycle_id).prefetch_related('seats')
        section_data = []
        for section in sections:
            filled_seats = section.seats.filter(is_filled=True).count()
            available_seats = section.total_seats - filled_seats
            section_data.append({
                'id': section.id,
                'section_name': section.section_name,
                'available_seats': available_seats
            })
        logger.debug(f"Found sections: {section_data}")
        return JsonResponse({'sections': section_data})
    logger.debug("No valid department_id or cycle_id provided")
    return JsonResponse({'sections': []})






# colleges/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CollegeProfile, AdmissionCycle
from .forms import AdmissionCycleForm

@login_required
def cycle_list(request):
    college_profile = get_object_or_404(CollegeProfile, user=request.user)
    cycles = AdmissionCycle.objects.filter(college=college_profile).order_by('-year')
    return render(request, 'colleges/cycle_list.html', {'college_profile': college_profile, 'cycles': cycles})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import AdmissionCycle
from .forms import AdmissionCycleForm

@login_required
def add_cycle(request):
    college_profile = get_object_or_404(CollegeProfile, user=request.user)
    if request.method == 'POST':
        form = AdmissionCycleForm(college=college_profile, data=request.POST)
        if form.is_valid():
            cycle = form.save(commit=False)
            cycle.college = college_profile
            cycle.save()
            messages.success(request, f"Admission cycle {cycle.year} created successfully!")
            return redirect('colleges:cycle_list')
    else:
        form = AdmissionCycleForm(college=college_profile)  # Pass college to form
    return render(request, 'colleges/add_cycle.html', {'form': form, 'college_profile': college_profile})
@login_required
def edit_cycle(request, cycle_id):
    college_profile = get_object_or_404(CollegeProfile, user=request.user)
    cycle = get_object_or_404(AdmissionCycle, id=cycle_id, college=college_profile)

    if request.method == 'POST':
        form = AdmissionCycleForm(college=college_profile, data=request.POST, instance=cycle)
        if form.is_valid():
            form.save()
            messages.success(request, f"Admission cycle {cycle.year} updated successfully!")
            return redirect('colleges:cycle_list')
    else:
        form = AdmissionCycleForm(college=college_profile, instance=cycle)  # Pass college here
    return render(request, 'colleges/edit_cycle.html', {'form': form, 'college_profile': college_profile, 'cycle': cycle})
@login_required
def delete_cycle(request, cycle_id):
    college_profile = get_object_or_404(CollegeProfile, user=request.user)
    cycle = get_object_or_404(AdmissionCycle, id=cycle_id, college=college_profile)

    if request.method == 'POST':
        cycle_name = cycle.year  # Capture year before deletion
        cycle.delete()
        messages.success(request, f"Admission cycle {cycle_name} deleted successfully.")
        return redirect('colleges:cycle_list')
    return render(request, 'colleges/delete_cycle.html', {'college_profile': college_profile, 'cycle': cycle})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.urls import reverse
from .models import CollegeProfile, AdmissionCycle, Degree, Department
from .forms import DegreeForm, DepartmentForm, SectionForm, CourseForm

@login_required
def degree_list(request):
    college_profile = get_object_or_404(CollegeProfile, user=request.user)
    selected_cycle_id = request.GET.get('cycle_id')
    selected_cycle = None
    if selected_cycle_id:
        selected_cycle = get_object_or_404(AdmissionCycle, id=selected_cycle_id, college=college_profile)
    degrees = college_profile.degrees.filter(cycle=selected_cycle) if selected_cycle else college_profile.degrees.all()
    cycles = AdmissionCycle.objects.filter(college=college_profile).order_by('-year')
    return render(request, 'colleges/degree_list.html', {
        'college_profile': college_profile,
        'degrees': degrees,
        'cycles': cycles,
        'selected_cycle_id': selected_cycle_id,
        'selected_cycle': selected_cycle,
    })

@login_required
def add_degree(request):
    college_profile = get_object_or_404(CollegeProfile, user=request.user)
    selected_cycle_id = request.GET.get('cycle_id')
    if not selected_cycle_id:
        messages.error(request, "Please select a cycle first.")
        return redirect('colleges:degree_list')
    selected_cycle = get_object_or_404(AdmissionCycle, id=selected_cycle_id, college=college_profile)
    if request.method == 'POST':
        form = DegreeForm(request.POST)
        if form.is_valid():
            degree = form.save(commit=False)
            degree.college = college_profile
            degree.cycle = selected_cycle
            try:
                degree.save()
                messages.success(request, f"Degree {degree.name} added successfully for cycle {selected_cycle.year}!")
                return redirect(reverse('colleges:degree_list') + f'?cycle_id={selected_cycle_id}')
            except IntegrityError:
                messages.error(request, f"Degree '{degree.name}' already exists for this college and cycle. Please choose a different name.")
                return redirect(reverse('colleges:add_degree') + f'?cycle_id={selected_cycle_id}')
    else:
        form = DegreeForm()
    return render(request, 'colleges/add_degree.html', {'form': form, 'college_profile': college_profile, 'selected_cycle': selected_cycle})

@login_required
def edit_degree(request, degree_id):
    college_profile = get_object_or_404(CollegeProfile, user=request.user)
    degree = get_object_or_404(Degree, id=degree_id, college=college_profile)
    selected_cycle_id = request.GET.get('cycle_id', degree.cycle.id)
    selected_cycle = get_object_or_404(AdmissionCycle, id=selected_cycle_id, college=college_profile)

    if request.method == 'POST':
        form = DegreeForm(request.POST, instance=degree)
        if form.is_valid():
            updated_degree = form.save(commit=False)
            updated_degree.college = college_profile
            updated_degree.cycle = selected_cycle  # Ensure cycle is preserved or updated
            try:
                updated_degree.save()
                messages.success(request, f"Degree {updated_degree.name} updated successfully for cycle {selected_cycle.year}!")
                return redirect(reverse('colleges:degree_list') + f'?cycle_id={selected_cycle_id}')
            except IntegrityError:
                messages.error(request, f"Degree '{updated_degree.name}' already exists for this college and cycle. Please choose a different name.")
                return redirect(reverse('colleges:edit_degree', args=[degree_id]) + f'?cycle_id={selected_cycle_id}')
    else:
        form = DegreeForm(instance=degree)
    return render(request, 'colleges/edit_degree.html', {
        'form': form,
        'college_profile': college_profile,
        'selected_cycle': selected_cycle,
        'degree': degree,
    })




@login_required
def delete_degree(request, degree_id):
    college_profile = get_object_or_404(CollegeProfile, user=request.user)
    degree = get_object_or_404(Degree, id=degree_id, college=college_profile)
    selected_cycle_id = request.GET.get('cycle_id', degree.cycle.id)
    selected_cycle = get_object_or_404(AdmissionCycle, id=selected_cycle_id, college=college_profile)

    if request.method == 'POST':
        # Check for dependencies
        if Department.objects.filter(degree=degree).exists():
            messages.error(request, f"Cannot delete '{degree.name}' because it has associated departments. Delete the departments first.")
            return redirect(reverse('colleges:degree_list') + f'?cycle_id={selected_cycle_id}')
        
        degree_name = degree.name  # Store for message
        degree.delete()
        messages.success(request, f"Degree '{degree_name}' deleted successfully!")
        return redirect(reverse('colleges:degree_list') + f'?cycle_id={selected_cycle_id}')

    return render(request, 'colleges/delete_degree.html', {
        'college_profile': college_profile,
        'degree': degree,
        'selected_cycle': selected_cycle,
    })




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CollegeProfile, AdmissionCycle, Degree, Department

@login_required
def department_list(request):
    college_profile = get_object_or_404(CollegeProfile, user=request.user)
    selected_cycle_id = request.GET.get('cycle_id')
    cycles = AdmissionCycle.objects.filter(college=college_profile).order_by('-year')
    cycle_degrees_departments = {}

    for cycle in cycles:
        # Fetch all degrees associated with the college for this cycle
        degrees = Degree.objects.filter(college=college_profile, cycle=cycle)
        degree_departments = {}
        for degree in degrees:
            # Fetch departments for this degree and cycle
            departments = Department.objects.filter(degree=degree, cycle=cycle)
            if departments.exists():
                degree_departments[degree] = departments
            else:
                degree_departments[degree] = []  # Include degree even if no departments
        if degrees.exists():  # Include cycle if it has degrees
            cycle_degrees_departments[cycle] = degree_departments

    context = {
        'college_profile': college_profile,
        'cycle_degrees_departments': cycle_degrees_departments,
        'cycles': cycles,
        'selected_cycle_id': selected_cycle_id,
    }
    return render(request, 'colleges/department_list.html', context)



from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from .models import CollegeProfile, AdmissionCycle, Degree, Department
from .forms import DepartmentForm

@login_required
def add_department(request, degree_id):
    college_profile = get_object_or_404(CollegeProfile, user=request.user)
    degree = get_object_or_404(Degree, id=degree_id, college=college_profile)
    selected_cycle_id = request.GET.get('cycle_id')
    if not selected_cycle_id:
        messages.error(request, "Please select a cycle first.")
        return redirect('colleges:department_list')
    selected_cycle = get_object_or_404(AdmissionCycle, id=selected_cycle_id, college=college_profile)
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save(commit=False)
            department.college = college_profile
            department.degree = degree
            department.cycle = selected_cycle
            try:
                department.save()
                messages.success(request, f"Department {department.name} added successfully for degree {degree.name}!")
                return redirect(reverse('colleges:department_list') + f'?cycle_id={selected_cycle_id}')
            except IntegrityError:
                messages.error(request, f"Department '{department.name}' already exists for this degree and cycle. Please choose a different name.")
                return redirect(reverse('colleges:add_department', args=[degree_id]) + f'?cycle_id={selected_cycle_id}')
    else:
        form = DepartmentForm()
    return render(request, 'colleges/add_department.html', {'form': form, 'college_profile': college_profile, 'degree': degree, 'selected_cycle': selected_cycle})



@login_required
def edit_department(request, department_id):
    college_profile = get_object_or_404(CollegeProfile, user=request.user)
    department = get_object_or_404(Department, id=department_id, college=college_profile)
    selected_cycle_id = request.GET.get('cycle_id')
    
    if not selected_cycle_id:
        messages.error(request, "Please select a cycle first.")
        return redirect('colleges:department_list')
    
    selected_cycle = get_object_or_404(AdmissionCycle, id=selected_cycle_id, college=college_profile)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            try:
                updated_department = form.save(commit=False)
                updated_department.college = college_profile
                updated_department.degree = department.degree  # Preserve original degree
                updated_department.cycle = selected_cycle  # Preserve cycle
                updated_department.save()
                messages.success(request, f"Department {updated_department.name} updated successfully!")
                return redirect(reverse('colleges:department_list') + f'?cycle_id={selected_cycle_id}')
            except IntegrityError:
                messages.error(request, f"Department '{updated_department.name}' already exists for this degree and cycle. Please choose a different name.")
    else:
        form = DepartmentForm(instance=department)
    
    return render(request, 'colleges/edit_department.html', {
        'form': form,
        'college_profile': college_profile,
        'department': department,
        'degree': department.degree,
        'selected_cycle': selected_cycle,
    })



@login_required
def delete_department(request, department_id):
    college_profile = get_object_or_404(CollegeProfile, user=request.user)
    department = get_object_or_404(Department, id=department_id, college=college_profile)
    selected_cycle_id = request.GET.get('cycle_id', department.cycle.id)
    selected_cycle = get_object_or_404(AdmissionCycle, id=selected_cycle_id, college=college_profile)

    if request.method == 'POST':
        # Check for dependencies
        if department.sections.exists():
            messages.error(request, f"Cannot delete '{department.name}' because it has associated sections. Delete the sections first.")
            return redirect(reverse('colleges:department_list') + f'?cycle_id={selected_cycle_id}')
        
        department_name = department.name  # Store for message
        department.delete()
        messages.success(request, f"Department '{department_name}' deleted successfully!")
        return redirect(reverse('colleges:department_list') + f'?cycle_id={selected_cycle_id}')

    return render(request, 'colleges/delete_department.html', {
        'college_profile': college_profile,
        'department': department,
        'degree': department.degree,
        'selected_cycle': selected_cycle,
    })






from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CollegeProfile, AdmissionCycle, Department, Section
import logging

logger = logging.getLogger(__name__)

@login_required
def section_list(request, department_id):
    college_profile = get_object_or_404(CollegeProfile, user=request.user)
    department = get_object_or_404(Department, id=department_id, college=college_profile)
    selected_cycle_id = request.GET.get('cycle_id')
    cycles = AdmissionCycle.objects.filter(college=college_profile, id=department.cycle.id).order_by('-year')  # Only department's cycle
    cycle_sections = {}

    logger.debug(f"Found cycles for department {department.name}: {cycles.count()}")
    for cycle in cycles:
        sections = Section.objects.filter(department=department, cycle=cycle)
        logger.debug(f"Sections for department {department.name} in cycle {cycle.year}: {sections.count()}")
        if sections.exists() or True:  # Always show the cycle
            cycle_sections[cycle] = sections

    context = {
        'college_profile': college_profile,
        'department': department,
        'cycle_sections': cycle_sections,
        'cycles': cycles,
        'selected_cycle_id': selected_cycle_id,
    }
    return render(request, 'colleges/section_list.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from .models import CollegeProfile, AdmissionCycle, Department, Section, Seat
from .forms import SectionForm

@login_required
def add_section(request, department_id):
    college_profile = get_object_or_404(CollegeProfile, user=request.user)
    department = get_object_or_404(Department, id=department_id, college=college_profile)
    selected_cycle_id = request.GET.get('cycle_id')
    if not selected_cycle_id:
        messages.error(request, "Please select a cycle first.")
        return redirect('colleges:section_list', department_id=department_id)
    selected_cycle = get_object_or_404(AdmissionCycle, id=selected_cycle_id, college=college_profile)
    if selected_cycle.id != department.cycle.id:
        messages.error(request, f"Cannot add section to {selected_cycle.year}. This department is linked to {department.cycle.year} cycle.")
        return redirect('colleges:section_list', department_id=department_id)
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            section.department = department
            section.cycle = selected_cycle
            try:
                section.save()
                current_seat_count = section.seats.count()
                if current_seat_count < section.total_seats:
                    for _ in range(section.total_seats - current_seat_count):
                        Seat.objects.create(section=section, is_filled=False)
                messages.success(request, f"Section {section.section_name} added successfully for department {department.name}!")
                return redirect(reverse('colleges:section_list', kwargs={'department_id': department_id}) + f'?cycle_id={selected_cycle_id}')
            except IntegrityError:
                messages.error(request, "An error occurred while saving the section. Please try again.")
    else:
        form = SectionForm()
    return render(request, 'colleges/add_section.html', {'form': form, 'college_profile': college_profile, 'department': department, 'selected_cycle': selected_cycle})

# colleges/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CollegeProfile, AdmissionCycle, Degree, Department, Course

@login_required
def course_list_all(request):
    college_profile = get_object_or_404(CollegeProfile, user=request.user)
    selected_cycle_id = request.GET.get('cycle_id')
    selected_cycle = None
    if selected_cycle_id:
        selected_cycle = get_object_or_404(AdmissionCycle, id=selected_cycle_id, college=college_profile)
    degrees = college_profile.degrees.filter(cycle=selected_cycle) if selected_cycle else college_profile.degrees.all()
    degree_department_courses = {}
    all_departments = {}
    all_departments_exist = False
    for degree in degrees:
        dept_courses = {}
        # Pre-filter departments
        departments = degree.departments.filter(cycle=selected_cycle) if selected_cycle else degree.departments.all()
        print(f"Degree: {degree.name}, Cycle: {selected_cycle.year if selected_cycle else 'All'}, Departments found: {departments.count()}")
        if departments.exists():
            all_departments_exist = True
            all_departments[degree] = departments
        for department in departments:
            # Pre-filter courses
            courses = department.courses.filter(cycle=selected_cycle) if selected_cycle else department.courses.all()
            if courses.exists():
                dept_courses[department] = courses
        if dept_courses or departments.exists():
            degree_department_courses[degree] = dept_courses
    cycles = AdmissionCycle.objects.filter(college=college_profile).order_by('-year')
    has_degrees = degrees.exists()
    has_departments = all_departments_exist
    return render(request, 'colleges/course_list_all.html', {
        'college_profile': college_profile,
        'degrees': degrees,
        'degree_department_courses': degree_department_courses,
        'all_departments': all_departments,
        'cycles': cycles,
        'selected_cycle_id': selected_cycle_id,
        'selected_cycle': selected_cycle,
        'has_degrees': has_degrees,
        'has_departments': has_departments,
    })

# colleges/views.py

# colleges/views.py (partial update for add_course)
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from .models import CollegeProfile, AdmissionCycle, Degree, Department
from .forms import CourseForm

@login_required
def add_course(request, degree_id, department_id):
    college_profile = get_object_or_404(CollegeProfile, user=request.user)
    degree = get_object_or_404(Degree, id=degree_id, college=college_profile)
    department = get_object_or_404(Department, id=department_id, college=college_profile, degree=degree)
    selected_cycle_id = request.GET.get('cycle_id')
    if not selected_cycle_id:
        messages.error(request, "Please select a cycle first.")
        return redirect('colleges:course_list_all')
    selected_cycle = get_object_or_404(AdmissionCycle, id=selected_cycle_id, college=college_profile)
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.degree = degree
            course.department = department
            course.cycle = selected_cycle
            try:
                course.save()
                messages.success(request, f"Course {course.name} added successfully for department {department.name}!")
                return redirect(reverse('colleges:course_list_all') + f'?cycle_id={selected_cycle_id}')
            except IntegrityError:
                messages.error(request, f"Course with code '{course.course_code}' and name '{course.name}' already exists in this department. Please choose different values.")
                return redirect(reverse('colleges:add_course', args=[degree_id, department_id]) + f'?cycle_id={selected_cycle_id}')
    else:
        form = CourseForm()
    return render(request, 'colleges/add_course.html', {
        'form': form,
        'college_profile': college_profile,
        'degree': degree,
        'department': department,
        'selected_cycle': selected_cycle,
    })





@login_required
def edit_course(request, course_id):
    college_profile = get_object_or_404(CollegeProfile, user=request.user)
    course = get_object_or_404(Course, id=course_id, department__college=college_profile)
    degree = course.degree
    department = course.department
    selected_cycle_id = request.GET.get('cycle_id')
    if not selected_cycle_id:
        messages.error(request, "Please select a cycle to edit the course.")
        return redirect('colleges:course_list_all')
    selected_cycle = get_object_or_404(AdmissionCycle, id=selected_cycle_id, college=college_profile)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            updated_course = form.save(commit=False)
            updated_course.degree = degree
            updated_course.department = department
            updated_course.cycle = selected_cycle
            try:
                updated_course.save()
                messages.success(request, f"Course '{updated_course.name}' updated successfully!")
                return redirect(reverse('colleges:course_list_all') + f'?cycle_id={selected_cycle_id}')
            except IntegrityError:
                messages.error(request, f"Course with code '{updated_course.course_code}' and name '{updated_course.name}' already exists in this department. Please choose different values.")
    else:
        form = CourseForm(instance=course)
    return render(request, 'colleges/edit_course.html', {
        'form': form,
        'college_profile': college_profile,
        'degree': degree,
        'department': department,
        'selected_cycle': selected_cycle,
        'course': course,
    })




@login_required
def delete_course(request, course_id):
    college_profile = get_object_or_404(CollegeProfile, user=request.user)
    course = get_object_or_404(Course, id=course_id, department__college=college_profile)
    selected_cycle_id = request.GET.get('cycle_id')
    if not selected_cycle_id:
        messages.error(request, "Please select a cycle to delete the course.")
        return redirect('colleges:course_list_all')
    try:
        course_name = course.name
        course.delete()
        messages.success(request, f"Course '{course_name}' deleted successfully!")
    except Exception as e:
        messages.error(request, f"Error deleting course: {str(e)}")
    return redirect(reverse('colleges:course_list_all') + f'?cycle_id={selected_cycle_id}')







# colleges/views.py or students/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import CollegeProfile, Degree, Department, Section, AdmissionCycle, Application
from .forms import ApplicationForm

# Student-facing views (no login required unless specified)
def college_list(request):
    colleges = CollegeProfile.objects.filter(user__is_active=True)
    filtered_colleges = colleges

    college_type = request.GET.get('college_type')
    state = request.GET.get('state')
    city = request.GET.get('city')

    if college_type:
        filtered_colleges = filtered_colleges.filter(college_type=college_type)
    if state:
        filtered_colleges = filtered_colleges.filter(state=state)
    if city:
        filtered_colleges = filtered_colleges.filter(city=city)

    unique_states = CollegeProfile.objects.values_list('state', flat=True).distinct().order_by('state')
    unique_cities = CollegeProfile.objects.values_list('city', flat=True).distinct().order_by('city')

    context = {
        'colleges': colleges,
        'filtered_colleges': filtered_colleges,
        'unique_states': unique_states,
        'unique_cities': unique_cities,
    }
    return render(request, 'colleges/college_list.html', context)

def college_detail(request, college_id):
    college = get_object_or_404(CollegeProfile, id=college_id, user__is_active=True)
    active_cycles = AdmissionCycle.objects.filter(college=college, is_active=True, is_archived=False).order_by('year')
    if active_cycles.exists():
        selected_cycle_id = request.GET.get('cycle_id')
        active_cycle = get_object_or_404(AdmissionCycle, id=selected_cycle_id, college=college) if selected_cycle_id else active_cycles.first()
        degrees = college.degrees.filter(cycle=active_cycle)
    else:
        active_cycle = None
        degrees = college.degrees.all()
    context = {
        'college': college,
        'degrees': degrees,
        'active_cycle': active_cycle,
        'active_cycles': active_cycles,
    }
    return render(request, 'colleges/college_detail.html', context)



def student_department_list(request, college_id, degree_id, cycle_id):
    college = get_object_or_404(CollegeProfile, id=college_id, user__is_active=True)
    degree = get_object_or_404(Degree, id=degree_id, college=college)
    cycle = get_object_or_404(AdmissionCycle, id=cycle_id, college=college)
    departments = degree.departments.filter(cycle=cycle)
    context = {
        'college': college,
        'degree': degree,
        'departments': departments,
        'cycle': cycle,  # Optional, for display in the template
    }
    return render(request, 'colleges/student_department_list.html', context)


def degree_detail(request, college_id, degree_id, department_id, cycle_id):
    college = get_object_or_404(CollegeProfile, id=college_id, user__is_active=True)
    degree = get_object_or_404(Degree, id=degree_id, college=college)
    department = get_object_or_404(Department, id=department_id, degree=degree, college=college)
    cycle = get_object_or_404(AdmissionCycle, id=cycle_id, college=college)
    courses = department.courses.filter(cycle=cycle) if cycle else department.courses.all()
    context = {
        'college': college,
        'degree': degree,
        'department': department,
        'courses': courses,
        'active_cycle': cycle,  # Use the URL-provided cycle
    }
    return render(request, 'colleges/degree_detail.html', context)


# New student-facing course list (no login required)
def student_course_list(request, college_id, degree_id, department_id):
    college = get_object_or_404(CollegeProfile, id=college_id, user__is_active=True)
    degree = get_object_or_404(Degree, id=degree_id, college=college)
    department = get_object_or_404(Department, id=department_id, degree=degree, college=college)
    active_cycle = AdmissionCycle.objects.filter(college=college, is_active=True, is_archived=False).first()
    courses = department.courses.filter(cycle=active_cycle) if active_cycle else []
    context = {
        'college': college,
        'degree': degree,
        'department': department,
        'courses': courses,
        'active_cycle': active_cycle,
    }
    return render(request, 'colleges/student_course_list.html', context)

@login_required
def department_seats(request, college_id, degree_id, department_id):
    if request.user.user_type != 'student':
        return HttpResponseForbidden("You are not authorized to access this page.")

    college = get_object_or_404(CollegeProfile, id=college_id, user__is_active=True)
    degree = get_object_or_404(Degree, id=degree_id, college=college)
    department = get_object_or_404(Department, id=department_id, degree=degree, college=college)

    active_cycles = AdmissionCycle.objects.filter(college=college, is_active=True, is_archived=False).order_by('year')
    if not active_cycles.exists():
        messages.error(request, "No active admission cycles are available for this college.")
        return redirect('colleges:degree_detail', college_id=college.id, degree_id=degree.id, department_id=department.id, cycle_id=active_cycles.first().id if active_cycles.first() else 1)

    selected_cycle_id = request.GET.get('cycle_id')
    selected_cycle = get_object_or_404(AdmissionCycle, id=selected_cycle_id, college=college) if selected_cycle_id else active_cycles.first()
    context = {'cycle_year': selected_cycle.year}

    sections = Section.objects.filter(department=department, cycle=selected_cycle).prefetch_related('seats')
    if not sections:
        messages.error(request, "No sections available for this department in the selected cycle.")
        return redirect('colleges:degree_detail', college_id=college.id, degree_id=degree.id, department_id=department.id, cycle_id=selected_cycle.id)

    for section in sections:
        section.filled_seats_dynamic = section.seats.filter(is_filled=True).count()
        section.available_seats = section.total_seats - section.filled_seats_dynamic

    active_applications = Application.objects.filter(student=request.user, department__college=college, status__in=['Pending', 'Approved'])
    withdrawn_applications = Application.objects.filter(student=request.user, department__college=college, status='Withdrawn')
    application_form = ApplicationForm(college=college, data=request.POST or None, request=request, initial={'cycle_id': selected_cycle.id, 'college_id': college_id})
    print(f"Debug: Selected Cycle ID: {selected_cycle.id}, Year: {selected_cycle.year}, Form Initial Cycle: {application_form.fields['cycle'].initial.id if application_form.fields['cycle'].initial else 'None'}")

    if request.method == 'POST' and 'apply' in request.POST:
        print(f"Debug: POST Selected Cycle ID: {selected_cycle.id}, Year: {selected_cycle.year}")
        if application_form.is_valid():
            section_id = request.POST.get('section')
            section = get_object_or_404(Section, id=section_id, department=department, cycle=selected_cycle)
            section.filled_seats_dynamic = section.seats.filter(is_filled=True).count()
            section.available_seats = section.total_seats - section.filled_seats_dynamic

            if active_applications.exists():
                active_app = active_applications.first()
                error_message = (
                    f"You already have an active application for {active_app.department.name} "
                    f"at {college.college_name} (Status: {active_app.status}). "
                    f"<a href='/students/application/withdraw/{active_app.id}/'>Withdraw</a> to apply again."
                )
                application_form.add_error(None, error_message)
            elif section.available_seats <= 0:
                application_form.add_error(None, "No available seats in the selected section.")
            else:
                application = application_form.save(commit=False)
                application.student = request.user
                application.department = department
                application.section = section
                application.cycle = selected_cycle
                application.status = 'Pending'
                application.save()
                application_submitted.send(sender=Application, student=request.user, institution=college, application=application)
                messages.success(request, "Application submitted successfully! Awaiting college approval.")
                return redirect('colleges:application_success')

    context.update({
        'college': college,
        'degree': degree,
        'department': department,
        'sections': sections,
        'application_form': application_form,
        'active_applications': active_applications,
        'withdrawn_applications': withdrawn_applications,
        'active_cycles': active_cycles,
        'selected_cycle_id': selected_cycle.id,
    })
    return render(request, 'colleges/department_seats.html', context)



from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import CollegeProfile, AdmissionCycle, Degree, Department, Application, Section
from .forms import ApplicationForm
from core.signals import application_submitted
import logging

logger = logging.getLogger(__name__)

@login_required
def apply_direct(request, college_id):
    if request.user.user_type != 'student':
        return HttpResponseForbidden("You are not authorized to access this page.")

    college = get_object_or_404(CollegeProfile, id=college_id, user__is_active=True)
    active_cycles = AdmissionCycle.objects.filter(college=college, is_active=True, is_archived=False).order_by('year')
    if not active_cycles.exists():
        messages.error(request, "No active admission cycles are available for this college.")
        return redirect('colleges:college_list')

    selected_cycle_id = request.GET.get('cycle_id')
    selected_cycle = get_object_or_404(AdmissionCycle, id=selected_cycle_id, college=college) if selected_cycle_id and AdmissionCycle.objects.filter(id=selected_cycle_id, college=college).exists() else active_cycles.first()

    active_applications = Application.objects.filter(student=request.user, department__college=college, status__in=['Pending', 'Approved'])
    withdrawn_applications = Application.objects.filter(student=request.user, department__college=college, status='Withdrawn')
    application_form = ApplicationForm(college=college, data=request.POST or None, request=request, initial={'college_id': college_id, 'cycle': selected_cycle.id})

    if request.method == 'POST' and 'apply' in request.POST:
        cycle_id = request.POST.get('cycle')
        if cycle_id:
            selected_cycle = get_object_or_404(AdmissionCycle, id=cycle_id, college=college)
        if application_form.is_valid():
            department_id = request.POST.get('department_id')
            section_id = request.POST.get('section_id')
            department = get_object_or_404(Department, id=department_id, college=college, cycle=selected_cycle)
            section = get_object_or_404(Section, id=section_id, department=department, cycle=selected_cycle)
            section.filled_seats_dynamic = section.seats.filter(is_filled=True).count()
            section.available_seats = section.total_seats - section.filled_seats_dynamic

            if active_applications.exists():
                active_app = active_applications.first()
                error_message = (
                    f"You already have an active application for {active_app.department.name} "
                    f"at {college.college_name} (Status: {active_app.status}). "
                    f"<a href='/students/application/withdraw/{active_app.id}/'>Withdraw</a> to apply again."
                )
                application_form.add_error(None, error_message)
            elif section.available_seats <= 0:
                application_form.add_error(None, "No available seats in the selected section.")
            else:
                application = application_form.save(commit=False)
                application.student = request.user
                application.department = department
                application.section = section
                application.cycle = selected_cycle
                application.status = 'Pending'
                application.save()
                application_submitted.send(sender=Application, student=request.user, institution=college, application=application)
                messages.success(request, "Application submitted successfully! Awaiting college approval.")
                return redirect('colleges:application_success')

    context = {
        'college': college,
        'active_cycles': active_cycles,
        'selected_cycle': selected_cycle,
        'application_form': application_form,
        'active_applications': active_applications,
        'withdrawn_applications': withdrawn_applications,
        'selected_cycle_id': selected_cycle.id,
    }
    logger.debug(f"Rendering apply_direct with cycles: {active_cycles.count()}, selected_cycle: {selected_cycle.year}")
    return render(request, 'colleges/apply_direct.html', context)



@login_required
def application_success(request):
    return render(request, 'colleges/application_success.html', context={})