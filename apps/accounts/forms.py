"""Forms for authentication, registration, user/role management, profile & prefs."""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .models import Role, UserPreference

User = get_user_model()


# A catalog of capability strings a Role can be granted.
PERMISSION_CHOICES = [
    ('projects.view', 'View projects'),
    ('projects.manage', 'Create/edit/delete projects'),
    ('tasks.view', 'View tasks'),
    ('tasks.manage', 'Create/edit/delete tasks'),
    ('meetings.manage', 'Manage meetings'),
    ('tickets.manage', 'Manage tickets'),
    ('invoices.view', 'View invoices'),
    ('invoices.manage', 'Manage invoices'),
    ('billing.manage', 'Manage subscription & billing'),
    ('users.view', 'View team members'),
    ('users.manage', 'Invite/manage users'),
    ('roles.manage', 'Manage roles & permissions'),
    ('branding.manage', 'Manage branding'),
    ('audit.view', 'View audit log'),
    ('reports.view', 'View reports & dashboards'),
]


class LoginForm(forms.Form):
    """Username-or-email + password login."""

    username = forms.CharField(
        label='Username or Email',
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True, 'autocomplete': 'username'}),
    )
    password = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )
    remember_me = forms.BooleanField(required=False, initial=False)


class RegistrationForm(forms.Form):
    """Tenant self-service onboarding: organization + admin account."""

    organization_name = forms.CharField(max_length=150)
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    password1 = forms.CharField(label='Password', strip=False, widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', strip=False, widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'The two password fields did not match.')
        if p1:
            validate_password(p1)
        return cleaned


class UserInviteForm(forms.Form):
    """Invite a new member by email + role."""

    email = forms.EmailField()
    role = forms.ModelChoiceField(queryset=Role.objects.none(), required=False)
    message = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            self.fields['role'].queryset = Role.objects.filter(tenant=tenant)

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if self.tenant and User.objects.filter(tenant=self.tenant, email__iexact=email).exists():
            raise forms.ValidationError('A member with this email already exists in your organization.')
        return email


class AcceptInviteForm(forms.Form):
    """Accept an invite: set name + password to create the account."""

    full_name = forms.CharField(max_length=150)
    password1 = forms.CharField(label='Password', strip=False, widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', strip=False, widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'The two password fields did not match.')
        if p1:
            validate_password(p1)
        return cleaned


class UserEditForm(forms.ModelForm):
    """Edit an existing member's details (tenant admin)."""

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'job_title', 'role', 'is_active', 'is_tenant_admin',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant is not None:
            self.fields['role'].queryset = Role.objects.filter(tenant=tenant)
        self.fields['role'].required = False

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        qs = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Another account already uses this email.')
        return email


class RoleForm(forms.ModelForm):
    """Create/edit a role with a multi-select permission catalog."""

    permissions = forms.MultipleChoiceField(
        choices=PERMISSION_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Role
        fields = ['name', 'description', 'permissions']

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        # Pre-fill the multi-select from the stored JSON list.
        if self.instance and self.instance.pk and isinstance(self.instance.permissions, list):
            self.fields['permissions'].initial = self.instance.permissions

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        qs = Role.objects.filter(tenant=self.tenant, name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('A role with this name already exists.')
        return name

    def clean_permissions(self):
        # Persist as a plain list of strings in the JSONField.
        return list(self.cleaned_data.get('permissions', []))


class ProfileForm(forms.ModelForm):
    """Edit your own profile."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'job_title', 'avatar']

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        qs = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Another account already uses this email.')
        return email


class PreferenceForm(forms.ModelForm):
    """Persist UI/theme preferences."""

    class Meta:
        model = UserPreference
        fields = [
            'theme', 'layout', 'sidebar_size', 'sidebar_color',
            'topbar', 'width', 'position', 'direction', 'preloader',
        ]
