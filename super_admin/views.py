from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from core.models import User
from django.contrib import messages
from core.signals import user_approved
from django.db.models import Q
from core.forms import AdminAddUserForm

@login_required
def dashboard(request):
    if request.user.user_type != 'super_admin':
        return redirect('core:login')

    # Get search query from GET parameters
    search_query = request.GET.get('search', '')

    # Statistics
    total_schools = User.objects.filter(user_type='school', is_approved=True).count()
    total_colleges = User.objects.filter(user_type='college', is_approved=True).count()
    total_students = User.objects.filter(user_type='student', is_approved=True).count()
    total_pending = User.objects.filter(is_approved=False).exclude(user_type='super_admin').count()

    # Pending approvals with search filter
    pending_users = User.objects.filter(is_approved=False).exclude(user_type='super_admin')
    if search_query:
        pending_users = pending_users.filter(
            Q(username__icontains=search_query)
        )

    # Approved users by role with search filter
    approved_schools = User.objects.filter(is_approved=True, user_type='school')
    approved_colleges = User.objects.filter(is_approved=True, user_type='college')
    approved_super_admins = User.objects.filter(is_approved=True, user_type='super_admin')
    approved_students = User.objects.filter(is_approved=True, user_type='student')

    if search_query:
        approved_schools = approved_schools.filter(
            Q(username__icontains=search_query)
        )
        approved_colleges = approved_colleges.filter(
            Q(username__icontains=search_query)
        )
        approved_super_admins = approved_super_admins.filter(
            Q(username__icontains=search_query)
        )
        approved_students = approved_students.filter(
            Q(username__icontains=search_query)
        )

    context = {
        'total_schools': total_schools,
        'total_colleges': total_colleges,
        'total_students': total_students,
        'total_pending': total_pending,
        'pending_users': pending_users,
        'approved_schools': approved_schools,
        'approved_colleges': approved_colleges,
        'approved_super_admins': approved_super_admins,
        'approved_students': approved_students,
        'search_query': search_query,
    }
    return render(request, 'super_admin/dashboard.html', context)

@login_required
def approve_user(request, user_id):
    if request.user.user_type != 'super_admin':
        return redirect('core:login')
    user = get_object_or_404(User, id=user_id)
    user.is_approved = True
    user.save()
    messages.success(request, f'{user.username} has been approved.')
    # Trigger the user_approved signal
    user_approved.send(sender=None, user=user)
    return redirect('super_admin:dashboard')

@login_required
def view_user(request, user_id):
    if request.user.user_type != 'super_admin':
        return redirect('core:login')
    user = get_object_or_404(User, id=user_id)
    context = {
        'user': user,
    }
    return render(request, 'super_admin/view_user.html', context)


# from django.contrib.auth.decorators import login_required
# from core.signals import user_approved

# @login_required
# def approve_user(request, user_id):
#     if request.user.user_type != 'super_admin':
#         return redirect('core:login')
#     user = get_object_or_404(User, id=user_id)
#     user.is_approved = True
#     user.save()
#     messages.success(request, f'{user.username} has been approved.')
#     # Trigger the user_approved signal
#     user_approved.send(sender=None, user=user)
#     return redirect('super_admin:dashboard')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from colleges.forms import CollegeRegistrationForm
from schools.forms import SchoolRegistrationForm
from students.forms import StudentRegistrationForm
from colleges.utils import STATES_DISTRICTS  # Import STATES_DISTRICTS
from .forms import UserTypeSelectionForm

@login_required
def add_user(request):
    if request.user.user_type != 'super_admin':
        return redirect('core:login')

    user_type_form = UserTypeSelectionForm(request.GET or None)
    selected_user_type = request.GET.get('user_type') or request.POST.get('user_type')

    # Initialize the appropriate registration form based on user type
    registration_form = None
    if selected_user_type == 'college':
        registration_form = CollegeRegistrationForm(request.POST or None, request.FILES or None)
    elif selected_user_type == 'school':
        registration_form = SchoolRegistrationForm(request.POST or None, request.FILES or None)
    elif selected_user_type == 'student':
        registration_form = StudentRegistrationForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if user_type_form.is_valid() and registration_form and registration_form.is_valid():
            registration_form.save()
            messages.success(request, 'User added successfully!')
            return redirect('super_admin:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')

    context = {
        'user_type_form': user_type_form,
        'registration_form': registration_form,
        'selected_user_type': selected_user_type,
        'states_districts': STATES_DISTRICTS,  # Pass STATES_DISTRICTS to the template
    }
    return render(request, 'super_admin/add_user.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.models import User  # Adjust based on your custom user model location
from core.forms import AdminAddUserForm  # Import from core app

@login_required
def manage_users(request):
    if request.user.user_type != 'super_admin':
        return redirect('core:login')

    search_query = request.GET.get('search', '')

    # Fetch users by role (include logged-in super admin this time)
    schools = User.objects.filter(user_type='school')
    colleges = User.objects.filter(user_type='college')
    students = User.objects.filter(user_type='student')
    super_admins = User.objects.filter(user_type='super_admin')

    # Apply search filter to all user roles
    if search_query:
        filter_condition = Q(username__icontains=search_query) | Q(email__icontains=search_query)
        schools = schools.filter(filter_condition)
        colleges = colleges.filter(filter_condition)
        students = students.filter(filter_condition)
        super_admins = super_admins.filter(filter_condition)

    context = {
        'schools': schools,
        'colleges': colleges,
        'students': students,
        'super_admins': super_admins,
        'search_query': search_query,
    }

    return render(request, 'super_admin/manage_users.html', context)

@login_required
def toggle_user_active(request, user_id):
    if request.user.user_type != 'super_admin':
        return redirect('core:login')
    user = get_object_or_404(User, id=user_id)
    if user.id == request.user.id:
        messages.error(request, 'You cannot deactivate yourself.')
    else:
        user.is_active = not user.is_active
        user.save()
        status = "activated" if user.is_active else "deactivated"
        messages.success(request, f'{user.username} has been {status}.')
    return redirect('super_admin:manage_users')

@login_required
def delete_user(request, user_id):
    if request.user.user_type != 'super_admin':
        return redirect('core:login')
    user = get_object_or_404(User, id=user_id)
    if user.id == request.user.id:
        messages.error(request, 'You cannot delete yourself.')
    else:
        user.delete()
        messages.success(request, f'{user.username} has been deleted.')
    return redirect('super_admin:manage_users')



from core.forms import UserUpdateForm
from core.models import User
from schools.models import SchoolProfile
from colleges.models import CollegeProfile
from students.models import StudentProfile
from colleges.utils import STATES_DISTRICTS
@login_required
def edit_user(request, user_id):
    if request.user.user_type != 'super_admin':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('core:login')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, f"{user.username}'s account details have been updated successfully.")
            return redirect('super_admin:manage_users')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserUpdateForm(instance=user)

    return render(request, 'super_admin/edit_user.html', {'user': user, 'user_form': user_form})

@login_required
def update_super_admin_details(request):
    if request.user.user_type != 'super_admin':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('core:login')

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account details have been updated successfully.")
            return redirect('super_admin:super_admin_details_updated')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'super_admin/update_super_admin_details.html', {'form': form})

@login_required
def super_admin_details_updated(request):
    if request.user.user_type != 'super_admin':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('core:login')
    return render(request, 'super_admin/super_admin_details_updated.html')

@login_required
def view_user_profile(request, user_id):
    if request.user.user_type != 'super_admin':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('core:login')

    user = get_object_or_404(User, id=user_id)
    profile = None
    if user.user_type == 'college':
        profile = get_object_or_404(CollegeProfile, user=user)
    elif user.user_type == 'school':
        profile = get_object_or_404(SchoolProfile, user=user)
    elif user.user_type == 'student':
        profile = get_object_or_404(StudentProfile, user=user)
    else:
        messages.error(request, "Invalid user type.")
        return redirect('super_admin:manage_users')

    return render(request, 'super_admin/view_user_profile.html', {
        'user': user,
        'profile': profile,
        'states_districts': STATES_DISTRICTS,
    })


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from colleges.forms import CollegeRegistrationForm
from schools.forms import SchoolRegistrationForm
from students.forms import StudentRegistrationForm
from core.models import User
from colleges.utils import STATES_DISTRICTS
from .forms import UserTypeSelectionForm
from .models import ActivityLog

# Existing add_user and edit_user views remain unchanged...

@login_required
def activity_logs(request):
    if request.user.user_type != 'super_admin':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('core:login')

    # Get the 10 most recent users based on last_login or last_logout
    recent_users = User.objects.exclude(user_type='super_admin').order_by('-last_login', '-last_logout')[:10]

    # Get schools, colleges, and students (15 each)
    schools = User.objects.filter(user_type='school').select_related('school_profile').order_by('-last_login', '-last_logout')[:15]
    colleges = User.objects.filter(user_type='college').select_related('college_profile').order_by('-last_login', '-last_logout')[:15]
    students = User.objects.filter(user_type='student').select_related('student_profile').order_by('-last_login', '-last_logout')[:15]

    context = {
        'recent_users': recent_users,
        'schools': schools,
        'colleges': colleges,
        'students': students,
    }
    return render(request, 'super_admin/activity_logs.html', context)