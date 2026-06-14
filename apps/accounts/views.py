"""Authentication, user & role management, profile and preferences views."""
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from apps.core.models import Tenant
from apps.core.utils import log_action

from .forms import (
    PERMISSION_CHOICES,
    AcceptInviteForm,
    LoginForm,
    PreferenceForm,
    ProfileForm,
    RegistrationForm,
    RoleForm,
    UserEditForm,
    UserInviteForm,
)
from .models import Role, User, UserInvite, UserPreference


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
        )
        if user is not None:
            login(request, user)
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            messages.success(request, f'Welcome back, {user.display_name}.')
            next_url = request.GET.get('next')
            return redirect(next_url or 'dashboard:index')
        messages.error(request, 'Invalid credentials. Please try again.')
    return render(request, 'auth/login.html', {'form': form, 'page_title': 'Sign In'})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been signed out.')
    return redirect('accounts:login')


def register_view(request):
    """Tenant onboarding: atomically create Tenant + admin User + supporting records."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        org_name = form.cleaned_data['organization_name'].strip()
        full_name = form.cleaned_data['full_name'].strip()
        email = form.cleaned_data['email']
        password = form.cleaned_data['password1']

        with transaction.atomic():
            tenant = Tenant.objects.create(
                name=org_name,
                slug=_unique_tenant_slug(org_name),
                contact_email=email,
            )
            admin_role = Role.objects.create(
                tenant=tenant,
                name='Administrator',
                description='Full access to the organization.',
                permissions=[code for code, _label in PERMISSION_CHOICES],
                is_system=True,
            )
            first, _, last = full_name.partition(' ')
            user = User.objects.create_user(
                username=_unique_username(email),
                email=email,
                password=password,
                first_name=first,
                last_name=last,
                tenant=tenant,
                is_tenant_admin=True,
                is_staff=False,
                role=admin_role,
            )
            tenant.owner = user
            tenant.save(update_fields=['owner'])
            UserPreference.objects.create(user=user)
            _provision_tenant_defaults(tenant)

        login(request, user)
        log_action(request, 'register', 'Tenant', tenant.name, 'Self-service onboarding')
        messages.success(request, f'Welcome to NavPMS, {user.display_name}! Your workspace is ready.')
        return redirect('dashboard:index')
    return render(request, 'auth/register.html', {'form': form, 'page_title': 'Create Account'})


def _unique_tenant_slug(name):
    base = slugify(name) or 'tenant'
    slug = base
    i = 2
    while Tenant.objects.filter(slug=slug).exists():
        slug = f'{base}-{i}'
        i += 1
    return slug


def _unique_username(email):
    base = slugify(email.split('@')[0]) or 'user'
    username = base
    i = 2
    while User.objects.filter(username__iexact=username).exists():
        username = f'{base}{i}'
        i += 1
    return username


def _provision_tenant_defaults(tenant):
    """Create a trial Subscription + BrandingSettings for a brand-new tenant."""
    from apps.tenants.models import BrandingSettings, Plan, Subscription

    today = timezone.now().date()
    plan = Plan.objects.filter(is_active=True).order_by('sort_order', 'price_monthly').first()
    Subscription.objects.get_or_create(
        tenant=tenant,
        defaults={
            'plan': plan,
            'status': Subscription.STATUS_TRIALING,
            'billing_cycle': 'monthly',
            'seats': plan.max_users if plan else 5,
            'started_at': today,
            'trial_ends_at': today + timedelta(days=14),
            'current_period_start': today,
            'current_period_end': today + timedelta(days=30),
        },
    )
    BrandingSettings.objects.get_or_create(tenant=tenant)


# ---------------------------------------------------------------------------
# Password reset (function-based, custom templates under templates/auth/)
# ---------------------------------------------------------------------------
password_reset = auth_views.PasswordResetView.as_view(
    template_name='auth/forgot_password.html',
    email_template_name='auth/password_reset_email.html',
    subject_template_name='auth/password_reset_subject.txt',
    success_url='/password-reset/done/',
)
password_reset_done = auth_views.PasswordResetDoneView.as_view(
    template_name='auth/password_reset_done.html',
)
password_reset_confirm = auth_views.PasswordResetConfirmView.as_view(
    template_name='auth/reset_password.html',
    success_url='/reset/done/',
)
password_reset_complete = auth_views.PasswordResetCompleteView.as_view(
    template_name='auth/password_reset_complete.html',
)


# ---------------------------------------------------------------------------
# Invites
# ---------------------------------------------------------------------------
def accept_invite(request, token):
    invite = get_object_or_404(UserInvite, token=token)
    if invite.status != UserInvite.STATUS_PENDING or invite.is_expired():
        if invite.is_expired() and invite.status == UserInvite.STATUS_PENDING:
            invite.status = UserInvite.STATUS_EXPIRED
            invite.save(update_fields=['status'])
        messages.error(request, 'This invitation is no longer valid.')
        return render(request, 'auth/invite_invalid.html', {'page_title': 'Invitation'})

    form = AcceptInviteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            full_name = form.cleaned_data['full_name'].strip()
            first, _, last = full_name.partition(' ')
            user = User.objects.create_user(
                username=_unique_username(invite.email),
                email=invite.email,
                password=form.cleaned_data['password1'],
                first_name=first,
                last_name=last,
                tenant=invite.tenant,
                role=invite.role,
            )
            UserPreference.objects.create(user=user)
            invite.status = UserInvite.STATUS_ACCEPTED
            invite.accepted_at = timezone.now()
            invite.save(update_fields=['status', 'accepted_at'])
        login(request, user)
        messages.success(request, f'Welcome to {invite.tenant.name}!')
        return redirect('dashboard:index')
    return render(request, 'auth/accept_invite.html', {
        'form': form, 'invite': invite, 'page_title': 'Accept Invitation',
    })


# ---------------------------------------------------------------------------
# User management (tenant-scoped)
# ---------------------------------------------------------------------------
@login_required
def user_list(request):
    qs = User.objects.filter(tenant=request.tenant).select_related('role')

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q)
            | Q(email__icontains=q) | Q(username__icontains=q)
        )

    role_id = request.GET.get('role', '').strip()
    if role_id:
        qs = qs.filter(role_id=role_id)

    status = request.GET.get('status', '').strip()
    if status == 'active':
        qs = qs.filter(is_active=True)
    elif status == 'inactive':
        qs = qs.filter(is_active=False)

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_title': 'User Management',
        'page_obj': page_obj,
        'users': page_obj.object_list,
        'roles': Role.objects.filter(tenant=request.tenant),
        'status_options': [('active', 'Active'), ('inactive', 'Inactive')],
        'pending_invites': UserInvite.objects.filter(
            tenant=request.tenant, status=UserInvite.STATUS_PENDING
        ),
        'total_count': paginator.count,
    }
    return render(request, 'accounts/user_list.html', context)


@login_required
def user_detail(request, pk):
    member = get_object_or_404(User, pk=pk, tenant=request.tenant)
    return render(request, 'accounts/user_detail.html', {
        'member': member, 'page_title': member.display_name,
    })


@login_required
def user_invite(request):
    form = UserInviteForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        invite = UserInvite.objects.create(
            tenant=request.tenant,
            email=form.cleaned_data['email'],
            role=form.cleaned_data.get('role'),
            invited_by=request.user,
            message=form.cleaned_data.get('message', ''),
            expires_at=timezone.now() + timedelta(days=7),
        )
        accept_url = settings.SITE_URL + reverse('accounts:accept_invite', kwargs={'token': invite.token})
        send_mail(
            subject=f'You are invited to join {request.tenant.name} on {settings.SITE_NAME}',
            message=(
                f'You have been invited to join {request.tenant.name}.\n\n'
                f'Accept your invitation: {accept_url}\n\n'
                f'{invite.message}'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invite.email],
            fail_silently=True,
        )
        log_action(request, 'invite', 'UserInvite', invite.email)
        messages.success(request, f'Invitation sent to {invite.email}.')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_invite.html', {'form': form, 'page_title': 'Invite User'})


@login_required
def user_edit(request, pk):
    member = get_object_or_404(User, pk=pk, tenant=request.tenant)
    form = UserEditForm(request.POST or None, instance=member, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_action(request, 'update', 'User', member.display_name)
        messages.success(request, 'Member updated successfully.')
        return redirect('accounts:user_detail', pk=member.pk)
    return render(request, 'accounts/user_form.html', {
        'form': form, 'member': member, 'page_title': f'Edit {member.display_name}',
    })


@login_required
def user_delete(request, pk):
    member = get_object_or_404(User, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        if member.pk == request.user.pk:
            messages.error(request, 'You cannot delete your own account.')
            return redirect('accounts:user_list')
        name = member.display_name
        member.delete()
        log_action(request, 'delete', 'User', name)
        messages.success(request, f'{name} was removed.')
        return redirect('accounts:user_list')
    return redirect('accounts:user_list')


@login_required
def user_toggle_active(request, pk):
    member = get_object_or_404(User, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        if member.pk == request.user.pk:
            messages.error(request, 'You cannot deactivate your own account.')
            return redirect('accounts:user_list')
        member.is_active = not member.is_active
        member.save(update_fields=['is_active'])
        log_action(request, 'toggle_active', 'User', member.display_name,
                   f'is_active={member.is_active}')
        state = 'activated' if member.is_active else 'deactivated'
        messages.success(request, f'{member.display_name} was {state}.')
    return redirect('accounts:user_list')


# ---------------------------------------------------------------------------
# Role management
# ---------------------------------------------------------------------------
@login_required
def role_list(request):
    qs = Role.objects.filter(tenant=request.tenant)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'accounts/role_list.html', {
        'page_title': 'Roles & Permissions',
        'page_obj': page_obj,
        'roles': page_obj.object_list,
        'total_count': paginator.count,
    })


@login_required
def role_create(request):
    form = RoleForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        role = form.save(commit=False)
        role.tenant = request.tenant
        role.save()
        log_action(request, 'create', 'Role', role.name)
        messages.success(request, f'Role "{role.name}" created.')
        return redirect('accounts:role_list')
    return render(request, 'accounts/role_form.html', {'form': form, 'page_title': 'Create Role'})


@login_required
def role_edit(request, pk):
    role = get_object_or_404(Role, pk=pk, tenant=request.tenant)
    form = RoleForm(request.POST or None, instance=role, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_action(request, 'update', 'Role', role.name)
        messages.success(request, f'Role "{role.name}" updated.')
        return redirect('accounts:role_list')
    return render(request, 'accounts/role_form.html', {
        'form': form, 'role': role, 'page_title': f'Edit {role.name}',
    })


@login_required
def role_delete(request, pk):
    role = get_object_or_404(Role, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        if role.is_system:
            messages.error(request, 'System roles cannot be deleted.')
            return redirect('accounts:role_list')
        name = role.name
        role.delete()
        log_action(request, 'delete', 'Role', name)
        messages.success(request, f'Role "{name}" deleted.')
        return redirect('accounts:role_list')
    return redirect('accounts:role_list')


# ---------------------------------------------------------------------------
# Profile & preferences
# ---------------------------------------------------------------------------
@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {
        'member': request.user, 'page_title': 'My Profile',
    })


@login_required
def profile_edit(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_action(request, 'update', 'Profile', request.user.display_name)
        messages.success(request, 'Profile updated.')
        return redirect('accounts:profile')
    return render(request, 'accounts/profile_edit.html', {'form': form, 'page_title': 'Edit Profile'})


@login_required
def change_password(request):
    form = PasswordChangeForm(user=request.user, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        log_action(request, 'change_password', 'User', request.user.display_name)
        messages.success(request, 'Your password was changed.')
        return redirect('accounts:profile')
    return render(request, 'accounts/change_password.html', {'form': form, 'page_title': 'Change Password'})


@login_required
def preferences_update(request):
    """Persist UI preferences (called via standard POST or HTMX/AJAX)."""
    preference, _ = UserPreference.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = PreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return HttpResponse(status=204)
            messages.success(request, 'Preferences saved.')
        elif request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponse(status=400)
    return redirect(request.META.get('HTTP_REFERER', reverse('dashboard:index')))
