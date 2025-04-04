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

def approve_user(request, user_id):
    if request.user.user_type != 'super_admin':
        return redirect('core:login')
    user = get_object_or_404(User, id=user_id)
    user.is_approved = True
    user.save()
    messages.success(request, f'{user.username} has been approved.')
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

def manage_users(request):
    if request.user.user_type != 'super_admin':
        return redirect('core:login')

    # Get search query from GET parameters
    search_query = request.GET.get('search', '')

    # Get users by role, excluding the current Super Admin
    schools = User.objects.filter(user_type='school').exclude(id=request.user.id)
    colleges = User.objects.filter(user_type='college').exclude(id=request.user.id)
    students = User.objects.filter(user_type='student').exclude(id=request.user.id)
    super_admins = User.objects.filter(user_type='super_admin').exclude(id=request.user.id)

    # Apply search filter (username or email)
    if search_query:
        schools = schools.filter(
            Q(username__icontains=search_query) | Q(email__icontains=search_query)
        )
        colleges = colleges.filter(
            Q(username__icontains=search_query) | Q(email__icontains=search_query)
        )
        students = students.filter(
            Q(username__icontains=search_query) | Q(email__icontains=search_query)
        )
        super_admins = super_admins.filter(
            Q(username__icontains=search_query) | Q(email__icontains=search_query)
        )

    context = {
        'schools': schools,
        'colleges': colleges,
        'students': students,
        'super_admins': super_admins,
        'search_query': search_query,
    }
    return render(request, 'super_admin/manage_users.html', context)

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
    else:
        form = AdminAddUserForm(instance=user)
    return render(request, 'super_admin/edit_user.html', {'form': form, 'user': user})