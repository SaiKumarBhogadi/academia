from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import User
from django.db.models import Q
from core.forms import AdminAddUserForm

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


from django.contrib.auth.decorators import login_required
from core.signals import user_approved

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

def add_user(request):
    if request.user.user_type != 'super_admin':
        return redirect('core:login')

    if request.method == 'POST':
        form = AdminAddUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User added successfully!')
            return redirect('super_admin:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminAddUserForm()
    return render(request, 'super_admin/add_user.html', {'form': form})


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

@login_required
def edit_user(request, user_id):
    if request.user.user_type != 'super_admin':
        return redirect('core:login')
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = AdminAddUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'{user.username} has been updated.')
            return redirect('super_admin:manage_users')
        else:
            messages.error(request, 'Please correct the errors below.')
            for field, errors in form.errors.items():
                print(f"Field: {field}, Errors: {errors}")  # Debug errors
    else:
        form = AdminAddUserForm(instance=user)
    return render(request, 'super_admin/edit_user.html', {'form': form, 'user': user})