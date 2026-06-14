"""
Template helpers for navigation and generic UI rendering.

Usage examples in templates:
    {% load nav_extras %}
    <a href="{% nav_link item %}">{{ item.label }}</a>
    <a href="{% submodule_link sub module %}">{{ sub.name }}</a>
    <span class="badge {% badge_class project.status %}">{{ project.get_status_display }}</span>
"""
from django import template
from django.urls import NoReverseMatch, reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def nav_link(context, item):
    """Resolve a simple nav item dict ({'url_name': ...}) to an href."""
    url_name = item.get('url_name')
    if not url_name:
        return '#'
    try:
        return reverse(url_name)
    except NoReverseMatch:
        return '#'


@register.simple_tag
def submodule_link(submodule, module):
    """
    Resolve a sub-module dict to its href.

    LIVE sub-modules reverse their own url_name; placeholders reverse
    core:module_placeholder with the (module_slug, sub_slug) kwargs.
    """
    url_name = submodule.get('url_name', 'core:module_placeholder')
    try:
        if submodule.get('is_live'):
            return reverse(url_name)
        return reverse(url_name, kwargs={
            'module_slug': module['slug'],
            'sub_slug': submodule['slug'],
        })
    except NoReverseMatch:
        return '#'


@register.simple_tag(takes_context=True)
def is_active_url(context, *url_names):
    """Return 'active' when the current path matches any of the given url names."""
    request = context.get('request')
    if request is None:
        return ''
    current = request.path
    for name in url_names:
        try:
            if reverse(name) == current:
                return 'active'
        except NoReverseMatch:
            continue
    return ''


@register.filter
def badge_class(value):
    """Map a status/priority/severity value to a semantic badge keyword."""
    mapping = {
        # Generic states
        'active': 'success', 'inactive': 'secondary',
        'draft': 'secondary', 'sent': 'info', 'paid': 'success',
        'overdue': 'danger', 'void': 'dark', 'partially_paid': 'warning',
        # Project / task status
        'not_started': 'secondary', 'in_progress': 'primary', 'on_hold': 'warning',
        'completed': 'success', 'cancelled': 'danger',
        'todo': 'secondary', 'review': 'info', 'done': 'success',
        # Tickets
        'open': 'primary', 'resolved': 'success', 'closed': 'secondary',
        # Priority
        'low': 'secondary', 'medium': 'info', 'high': 'warning', 'urgent': 'danger',
        # Severity / alerts
        'info': 'info', 'warning': 'warning', 'critical': 'danger',
        # Subscription
        'trialing': 'info', 'past_due': 'warning', 'canceled': 'secondary', 'expired': 'danger',
        # Invites
        'pending': 'warning', 'accepted': 'success', 'revoked': 'danger',
    }
    return mapping.get(str(value), 'secondary')


@register.filter
def get_item(dictionary, key):
    """Dictionary lookup by variable key in templates: {{ mydict|get_item:key }}."""
    if hasattr(dictionary, 'get'):
        return dictionary.get(key)
    return None


@register.filter
def percent_of(value, total):
    """Return value as an integer percentage of total (safe against zero)."""
    try:
        total = float(total)
        if total == 0:
            return 0
        return int(round(float(value) / total * 100))
    except (TypeError, ValueError):
        return 0
