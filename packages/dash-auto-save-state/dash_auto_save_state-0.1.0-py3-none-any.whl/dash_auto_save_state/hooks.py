"""
Dash hooks implementation for auto-save functionality
"""

from dash import html
from .auto_save_state import AutoSaveState


def auto_save_state_hook(
        storage_key='dash_auto_save_state',
        save_interval=1000,
        excluded_components=None,
        sync_across_tabs=True,
        debug=False
):
    """
    Dash hook function that returns the auto-save components.

    This function can be used directly in the Dash app layout to enable
    auto-save functionality.

    Parameters:
    -----------
    storage_key : str, default "dash_auto_save_state"
        Key used for localStorage storage
    save_interval : int, default 1000
        Debounce interval in milliseconds for saving state
    excluded_components : list, optional
        List of component IDs to exclude from auto-save
    sync_across_tabs : bool, default True
        Whether to sync state across browser tabs
    debug : bool, default False
        Enable debug logging

    Returns:
    --------
    html.Div containing the auto-save components

    Example:
    --------
    from dash import Dash, html, dcc
    from dash_auto_save_state import auto_save_state_hook

    app = Dash(__name__)

    app.layout = html.Div([
        auto_save_state_hook(debug=True),
        dcc.Input(id="my-input", type="text", placeholder="Type something..."),
        html.Div(id="output")
    ])
    """
    auto_save = AutoSaveState(
        storage_key=storage_key,
        save_interval=save_interval,
        excluded_components=excluded_components or [],
        sync_across_tabs=sync_across_tabs,
        debug=debug
    )

    # Return the storage components wrapped in a div
    return html.Div([
        auto_save.get_storage_component(),
        html.Script(auto_save.get_client_side_callback_code()),
    ], id='auto-save-hook-container', style={'display': 'none'})


# Alternative simplified hook for basic usage
def simple_auto_save_hook(debug=False):
    """
    Simplified version of auto_save_state_hook with default settings.

    Parameters:
    -----------
    debug : bool, default False
        Enable debug logging

    Returns:
    --------
    html.Div containing the auto-save components
    """
    return auto_save_state_hook(debug=debug)


# Hook for sensitive data (excluded components)
def secure_auto_save_hook(excluded_components=None, debug=False):
    """
    Auto-save hook with security considerations.
    Excludes password fields and other sensitive components by default.

    Parameters:
    -----------
    excluded_components : list, optional
        Additional component IDs to exclude (beyond default sensitive ones)
    debug : bool, default False
        Enable debug logging

    Returns:
    --------
    html.Div containing the auto-save components
    """
    default_excluded = [
        'password',
        'pwd',
        'pass',
        'secret',
        'token',
        'key',
        'credit-card',
        'ssn',
        'social-security'
    ]

    if excluded_components:
        default_excluded.extend(excluded_components)

    return auto_save_state_hook(
        excluded_components=default_excluded,
        debug=debug
    )
