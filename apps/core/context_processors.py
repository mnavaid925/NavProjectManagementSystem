"""Template context processors: navigation tree + UI preferences."""
from .navigation import get_navigation

# Default UI preference values mirrored from accounts.UserPreference defaults.
DEFAULT_UI_PREFS = {
    'theme': 'light',
    'layout': 'vertical',
    'sidebar_size': 'default',
    'sidebar_color': 'light',
    'topbar': 'light',
    'width': 'fluid',
    'position': 'fixed',
    'direction': 'ltr',
    'preloader': True,
}


def navigation(request):
    """Expose the sidebar tree and current tenant to every template."""
    return {
        'nav_sections': get_navigation()['sections'],
        'current_tenant': getattr(request, 'tenant', None),
    }


def ui_preferences(request):
    """
    Expose the current user's UI preferences (or sensible defaults) so the base
    template can set server-side body data-* attributes (theme/layout/etc).
    """
    prefs = dict(DEFAULT_UI_PREFS)
    user = getattr(request, 'user', None)
    if user is not None and user.is_authenticated:
        preference = getattr(user, 'preference', None)
        if preference is not None:
            prefs = {
                'theme': preference.theme,
                'layout': preference.layout,
                'sidebar_size': preference.sidebar_size,
                'sidebar_color': preference.sidebar_color,
                'topbar': preference.topbar,
                'width': preference.width,
                'position': preference.position,
                'direction': preference.direction,
                'preloader': preference.preloader,
            }
    return {'ui_prefs': prefs}
