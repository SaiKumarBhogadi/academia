# colleges/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CollegeProfile, Department, Degree, Course
from .forms import CollegeProfileForm, DepartmentForm, DegreeForm, CourseForm

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

@login_required
def dashboard(request):
    if not hasattr(request.user, 'college_profile'):
        messages.error(request, "You need to create a college profile first.")
        return redirect('colleges:college_profile')

    college_profile = request.user.college_profile
    degrees = college_profile.degrees.all()
    return render(request, 'colleges/dashboard.html', {
        'college_profile': college_profile,
        'degrees': degrees,
    })

@login_required
def add_degrees(request):
    if not hasattr(request.user, 'college_profile'):
        messages.error(request, "You need to create a college profile first.")
        return redirect('colleges:college_profile')

    college = request.user.college_profile
    if request.method == 'POST':
        form = DegreeForm(request.POST)
        if form.is_valid():
            degree = form.save(commit=False)
            degree.college = college
            degree.save()
            messages.success(request, "Degree added successfully!")
            return redirect('colleges:dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DegreeForm()

    return render(request, 'colleges/add_degrees.html', {
        'form': form,
        'college': college,
    })

@login_required
def edit_degree(request, degree_id):
    if not hasattr(request.user, 'college_profile'):
        messages.error(request, "You need to create a college profile first.")
        return redirect('colleges:college_profile')

    college = request.user.college_profile
    degree = get_object_or_404(Degree, id=degree_id, college=college)
    if request.method == 'POST':
        form = DegreeForm(request.POST, instance=degree)
        if form.is_valid():
            form.save()
            messages.success(request, "Degree updated successfully!")
            return redirect('colleges:dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DegreeForm(instance=degree)

    return render(request, 'colleges/edit_degree.html', {
        'form': form,
        'degree': degree,
        'college': college,
    })

@login_required
def link_departments(request, degree_id):
    if not hasattr(request.user, 'college_profile'):
        messages.error(request, "You need to create a college profile first.")
        return redirect('colleges:college_profile')

    college = request.user.college_profile
    degree = get_object_or_404(Degree, id=degree_id, college=college)
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save(commit=False)
            department.college = college
            department.degree = degree
            department.save()
            messages.success(request, "Department added successfully!")
            return redirect('colleges:dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DepartmentForm()

    return render(request, 'colleges/link_departments.html', {
        'form': form,
        'degree': degree,
        'college': college,
    })

@login_required
def edit_department(request, degree_id, department_id):
    if not hasattr(request.user, 'college_profile'):
        messages.error(request, "You need to create a college profile first.")
        return redirect('colleges:college_profile')

    college = request.user.college_profile
    degree = get_object_or_404(Degree, id=degree_id, college=college)
    department = get_object_or_404(Department, id=department_id, degree=degree, college=college)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, "Department updated successfully!")
            return redirect('colleges:dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DepartmentForm(instance=department)

    return render(request, 'colleges/edit_department.html', {
        'form': form,
        'department': department,
        'degree': degree,
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
    courses = department.courses.all()
    return render(request, 'colleges/course_list_all.html', {
        'college': college,
        'degree': degree,
        'department': department,
        'courses': courses,
    })

@login_required
def add_course(request, degree_id, department_id):
    if not hasattr(request.user, 'college_profile'):
        messages.error(request, "You need to create a college profile first.")
        return redirect('colleges:college_profile')

    college = request.user.college_profile
    degree = get_object_or_404(Degree, id=degree_id, college=college)
    department = get_object_or_404(Department, id=department_id, degree=degree, college=college)
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.degree = degree
            course.department = department
            course.save()
            messages.success(request, "Course added successfully!")
            return redirect('colleges:course_list', degree_id=degree.id, department_id=department.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CourseForm()

    return render(request, 'colleges/add_course.html', {
        'form': form,
        'degree': degree,
        'department': department,
        'college': college,
    })

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
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully!")
            return redirect('colleges:course_list', degree_id=degree.id, department_id=department.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CourseForm(instance=course)

    return render(request, 'colleges/edit_course.html', {
        'form': form,
        'course': course,
        'degree': degree,
        'department': department,
        'college': college,
    })

# Student-facing views
def college_list(request):
    colleges = CollegeProfile.objects.filter(user__is_active=True)
    return render(request, 'colleges/college_list.html', {
        'colleges': colleges,
    })

def college_detail(request, college_id):
    college = get_object_or_404(CollegeProfile, id=college_id, user__is_active=True)
    degrees = college.degrees.all()
    return render(request, 'colleges/college_detail.html', {
        'college': college,
        'degrees': degrees,
    })

def student_department_list(request, college_id, degree_id):
    college = get_object_or_404(CollegeProfile, id=college_id, user__is_active=True)
    degree = get_object_or_404(Degree, id=degree_id, college=college)
    departments = degree.departments.all()
    return render(request, 'colleges/student_department_list.html', {
        'college': college,
        'degree': degree,
        'departments': departments,
    })

def degree_detail(request, college_id, degree_id, department_id):
    college = get_object_or_404(CollegeProfile, id=college_id, user__is_active=True)
    degree = get_object_or_404(Degree, id=degree_id, college=college)
    department = get_object_or_404(Department, id=department_id, degree=degree, college=college)
    courses = department.courses.all()
    return render(request, 'colleges/degree_detail.html', {
        'college': college,
        'degree': degree,
        'department': department,
        'courses': courses,
    })



# colleges/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import CollegeProfile, Degree, Department, Course
from .forms import DegreeForm, DepartmentForm, CourseForm

# Existing views (college_profile, dashboard, add_degrees, edit_degree, link_departments, edit_department, course_list, add_course, edit_course) remain unchanged

def degree_list(request):
    college_profile = get_object_or_404(CollegeProfile, user=request.user)
    degrees = college_profile.degrees.all()
    return render(request, 'colleges/degree_list.html', {
        'college_profile': college_profile,
        'degrees': degrees,
    })

def department_list(request):
    college_profile = get_object_or_404(CollegeProfile, user=request.user)
    degrees = college_profile.degrees.all()
    # Create a dictionary of degrees with their departments
    degree_departments = {degree: degree.departments.all() for degree in degrees}
    return render(request, 'colleges/department_list.html', {
        'college_profile': college_profile,
        'degrees': degrees,
        'degree_departments': degree_departments,
    })

def course_list_all(request):
    college_profile = get_object_or_404(CollegeProfile, user=request.user)
    degrees = college_profile.degrees.all()
    # Create a nested structure: degree -> departments -> courses
    degree_department_courses = {}
    for degree in degrees:
        departments = degree.departments.all()
        department_courses = {dept: dept.courses.all() for dept in departments}
        degree_department_courses[degree] = department_courses
    # For the "Add Course" dropdown
    departments = college_profile.departments.all()
    return render(request, 'colleges/course_list_all.html', {
        'college_profile': college_profile,
        'degrees': degrees,
        'degree_department_courses': degree_department_courses,
        'departments': departments,
    })