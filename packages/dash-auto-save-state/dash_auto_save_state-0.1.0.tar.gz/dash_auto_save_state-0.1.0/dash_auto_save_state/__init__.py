"""
Dash Auto Save State Plugin

A Dash hook that automatically saves and restores component states to prevent data loss.
Supports localStorage persistence, cross-tab synchronization, and configurable exclusions.
"""

from .auto_save_state import AutoSaveState
from .hooks import auto_save_state_hook

__version__ = '0.1.0'
__author__ = 'Artem Liubarski'
__email__ = 'feanor1992@gmail.com'


# Main function to register the hook
def enable_auto_save(
        app=None,
        storage_key='dash_auto_save_state',
        save_interval=1000,
        excluded_components=None,
        sync_across_tabs=True,
        debug=False
):
    """
    Enable auto-save functionality for a Dash app.
    :param app: dash.Dash, optional
        The Dash app instance. If None, will be applied globally.
    :param storage_key: str, default "dash_auto_save_state"
        Key used for localStorage storage
    :param save_interval: int, default 1000
        Debounce interval in milliseconds for saving state
    :param excluded_components: list, optional
        List of component IDs to exclude from auto-save
    :param sync_across_tabs: bool, default True
        Whether to sync state across browser tabs
    :param debug: bool, default False
        Enable debug logging
    :return: AutoSaveState instance
    """
    auto_save = AutoSaveState(
        storage_key=storage_key,
        save_interval=save_interval,
        excluded_components=excluded_components or [],
        sync_across_tabs=sync_across_tabs,
        debug=debug
    )
    if app:
        auto_save.register_with_app(app)

    return auto_save


# For backwards compatibility
register_auto_save = enable_auto_save

__all__ = [
    'AutoSaveState',
    'auto_save_state_hook',
    'enable_auto_save',
    'register_auto_save'
]
