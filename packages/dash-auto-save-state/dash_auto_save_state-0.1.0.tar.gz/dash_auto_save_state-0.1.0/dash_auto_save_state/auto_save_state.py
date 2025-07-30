"""
Main AutoSaveState class implementation
"""

import json
from typing import List, Dict, Any, Optional, Union

import dash
from dash import html, callback, Input, Output, State, ALL, MATCH, ctx
from dash.exceptions import PreventUpdate


class AutoSaveState:
    """
    Automatically saves and restores Dash component states to localStorage.
    """
    def __init__(
            self,
            storage_key: str = "dash_auto_save_state",
            save_interval: int = 1000,
            excluded_components: Optional[List[str]] = None,
            sync_across_tabs: bool = True,
            debug: bool = False
    ):
        self.storage_key = storage_key
        self.save_interval = save_interval
        self.excluded_components = excluded_components or []
        self.sync_across_tabs = sync_across_tabs
        self.debug = debug
        self._registered_apps = []

    def get_storage_component(self) -> html.Div:
        """
        Returns the storage component that handles localStorage operations.
        """
        return html.Div([
            # Hidden storage component for saving state
            html.Div(
                id={
                    'type': 'auto-save-storage',
                    'index': 'main'
                },
                style={'display': 'none'},
                **{'data-storage-key': self.storage_key}
            ),
            # Hidden component for loading state on app start
            html.Div(
                id={
                    'type': 'auto-save-loader',
                    'index': 'main'
                },
                style={'display': 'none'}
            ),
            # Tab synchronization component (if enabled)
            html.Div(
                id={
                    'type': 'auto-save-sync',
                    'index': 'main'
                },
                style={'display': 'none'}
            ) if self.sync_across_tabs else html.Div(),
        ])

    def get_client_side_callback_code(self) -> str:
        """
        Returns the JavaScript code for client-side callbacks.
        """
        return f"""
        window.dash_clientside = Object.assign({{}}, window.dash_clientside, {{
            auto_save_state: {{
                // Save state to localStorage
                save_state: function(trigger, ...component_values) {{
                    if (!trigger) return window.dash_clientside.no_update;

                    const storage_key = '{self.storage_key}';
                    const excluded = {json.dumps(self.excluded_components)};
                    const debug = {json.dumps(self.debug)};

                    // Get all component IDs from trigger context
                    const triggered = window.dash_clientside.callback_context.triggered;
                    if (!triggered || triggered.length === 0) {{
                        return window.dash_clientside.no_update;
                    }}

                    // Build state object
                    const state = {{}};
                    const components = document.querySelectorAll('[id]');

                    components.forEach(function(element) {{
                        const id = element.id;
                        if (id && !excluded.includes(id) && !id.includes('auto-save')) {{
                            try {{
                                // Get component value based on type
                                let value = null;
                                if (element.type === 'text' || element.type === 'email' || element.type === 'password') {{
                                    value = element.value;
                                }} else if (element.type === 'checkbox' || element.type === 'radio') {{
                                    value = element.checked;
                                }} else if (element.tagName === 'SELECT') {{
                                    value = Array.from(element.selectedOptions).map(opt => opt.value);
                                    if (!element.multiple && value.length === 1) value = value[0];
                                }} else if (element.tagName === 'TEXTAREA') {{
                                    value = element.value;
                                }}

                                if (value !== null) {{
                                    state[id] = value;
                                }}
                            }} catch (e) {{
                                if (debug) console.warn('Auto-save: Error getting value for', id, e);
                            }}
                        }}
                    }});

                    // Save to localStorage
                    try {{
                        localStorage.setItem(storage_key, JSON.stringify({{
                            timestamp: Date.now(),
                            state: state
                        }}));

                        if (debug) {{
                            console.log('Auto-save: Saved state', state);
                        }}
                    }} catch (e) {{
                        if (debug) console.error('Auto-save: Failed to save state', e);
                    }}

                    return window.dash_clientside.no_update;
                }},

                // Load state from localStorage
                load_state: function(trigger) {{
                    if (!trigger) return {{}};

                    const storage_key = '{self.storage_key}';
                    const debug = {json.dumps(self.debug)};

                    try {{
                        const saved_data = localStorage.getItem(storage_key);
                        if (saved_data) {{
                            const parsed = JSON.parse(saved_data);
                            if (debug) {{
                                console.log('Auto-save: Loaded state', parsed.state);
                            }}
                            return parsed.state || {{}};
                        }}
                    }} catch (e) {{
                        if (debug) console.error('Auto-save: Failed to load state', e);
                    }}

                    return {{}};
                }},

                // Sync across tabs (storage event listener)
                sync_tabs: function(trigger) {{
                    if (!{json.dumps(self.sync_across_tabs)}) {{
                        return window.dash_clientside.no_update;
                    }}

                    const storage_key = '{self.storage_key}';
                    const debug = {json.dumps(self.debug)};

                    // Listen for storage changes from other tabs
                    window.addEventListener('storage', function(e) {{
                        if (e.key === storage_key && e.newValue) {{
                            try {{
                                const new_state = JSON.parse(e.newValue).state;
                                if (debug) {{
                                    console.log('Auto-save: Syncing from other tab', new_state);
                                }}

                                // Apply state to current tab
                                Object.keys(new_state).forEach(function(id) {{
                                    const element = document.getElementById(id);
                                    if (element) {{
                                        try {{
                                            if (element.type === 'text' || element.type === 'email' || element.type === 'password') {{
                                                element.value = new_state[id];
                                            }} else if (element.type === 'checkbox' || element.type === 'radio') {{
                                                element.checked = new_state[id];
                                            }} else if (element.tagName === 'SELECT') {{
                                                const values = Array.isArray(new_state[id]) ? new_state[id] : [new_state[id]];
                                                Array.from(element.options).forEach(function(option) {{
                                                    option.selected = values.includes(option.value);
                                                }});
                                            }} else if (element.tagName === 'TEXTAREA') {{
                                                element.value = new_state[id];
                                            }}
                                        }} catch (err) {{
                                            if (debug) console.warn('Auto-save: Error syncing', id, err);
                                        }}
                                    }}
                                }});
                            }} catch (err) {{
                                if (debug) console.error('Auto-save: Sync error', err);
                            }}
                        }}
                    }});

                    return window.dash_clientside.no_update;
                }}
            }}
        }});
        """

    def register_with_app(self, app: dash.Dash):
        """
        Register the auto-save functionality with a Dash app.
        """
        if app in self._registered_apps:
            return

        self._registered_apps.append(app)

        # Add the JavaScript code to the app
        app.clientside_callback(
            self.get_client_side_callback_code(),
            Output(
                {'type': 'auto-save-storage', 'index': 'main'},
                'children'
            ),
            Input(
                {'type': 'auto-save-storage', 'index': 'main'},
                'id'
            ),
            prevent_initial_call=False
        )

        # Add storage event listener for tab sync
        if self.sync_across_tabs:
            app.clientside_callback(
                'auto_save_state.sync_tabs',
                Output(
                    {'type': 'auto-save-sync', 'index': 'main'},
                    'children'
                ),
                Input(
                    {'type': 'auto-save-sync', 'index': 'main'},
                    'id'
                ),
                prevent_initial_call=False
            )

    def clear_saved_state(self, app: Optional[dash.Dash] = None):
        """
        Clear saved state from localStorage.
        This should be called from a server-side callback.
        """
        # This would typically be implemented as a clientside callback
        # that can be triggered from server-side
        pass

    def get_saved_state_info(self) -> Dict[str, Any]:
        """
        Get information about the saved state.
        This is a utility method for debugging.
        """
        return {
            'storage_key': self.storage_key,
            'save_interval': self.save_interval,
            'excluded_components': self.excluded_components,
            'sync_across_tabs': self.sync_across_tabs,
            'debug': self.debug
        }
