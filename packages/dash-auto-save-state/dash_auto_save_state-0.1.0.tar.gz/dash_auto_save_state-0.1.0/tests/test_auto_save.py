"""
Unit tests for dash-auto-save-state
"""

import pytest
from dash import Dash, html, dcc
from dash_auto_save_state import AutoSaveState, enable_auto_save, auto_save_state_hook


class TestAutoSaveState:
    """Test cases for AutoSaveState class"""

    def test_init_default_values(self):
        """Test AutoSaveState initialization with default values"""
        auto_save = AutoSaveState()

        assert auto_save.storage_key == "dash_auto_save_state"
        assert auto_save.save_interval == 1000
        assert auto_save.excluded_components == []
        assert auto_save.sync_across_tabs == True
        assert auto_save.debug == False

    def test_init_custom_values(self):
        """Test AutoSaveState initialization with custom values"""
        auto_save = AutoSaveState(
            storage_key="custom_key",
            save_interval=2000,
            excluded_components=["password"],
            sync_across_tabs=False,
            debug=True
        )

        assert auto_save.storage_key == "custom_key"
        assert auto_save.save_interval == 2000
        assert auto_save.excluded_components == ["password"]
        assert auto_save.sync_across_tabs == False
        assert auto_save.debug == True

    def test_get_storage_component(self):
        """Test storage component generation"""
        auto_save = AutoSaveState()
        component = auto_save.get_storage_component()

        assert isinstance(component, html.Div)
        assert len(component.children) >= 2  # Should have at least storage and loader

    def test_get_client_side_callback_code(self):
        """Test client-side callback code generation"""
        auto_save = AutoSaveState(debug=True)
        code = auto_save.get_client_side_callback_code()

        assert "window.dash_clientside" in code
        assert "auto_save_state" in code
        assert "save_state" in code
        assert "load_state" in code
        assert auto_save.storage_key in code

    def test_register_with_app(self):
        """Test app registration"""
        app = Dash(__name__)
        auto_save = AutoSaveState()

        # Should not raise an exception
        auto_save.register_with_app(app)

        # Should be registered
        assert app in auto_save._registered_apps

        # Should not register twice
        auto_save.register_with_app(app)
        assert len(auto_save._registered_apps) == 1

    def test_get_saved_state_info(self):
        """Test saved state info retrieval"""
        auto_save = AutoSaveState(
            storage_key="test_key",
            debug=True
        )

        info = auto_save.get_saved_state_info()

        assert info["storage_key"] == "test_key"
        assert info["debug"] == True
        assert "save_interval" in info
        assert "excluded_components" in info
        assert "sync_across_tabs" in info


class TestUtilityFunctions:
    """Test utility functions"""

    def test_enable_auto_save_without_app(self):
        """Test enable_auto_save without app parameter"""
        auto_save = enable_auto_save()

        assert isinstance(auto_save, AutoSaveState)
        assert auto_save.storage_key == "dash_auto_save_state"

    def test_enable_auto_save_with_app(self):
        """Test enable_auto_save with app parameter"""
        app = Dash(__name__)
        auto_save = enable_auto_save(app, debug=True)

        assert isinstance(auto_save, AutoSaveState)
        assert app in auto_save._registered_apps
        assert auto_save.debug == True

    def test_enable_auto_save_custom_params(self):
        """Test enable_auto_save with custom parameters"""
        auto_save = enable_auto_save(
            storage_key="custom_test",
            save_interval=5000,
            excluded_components=["secret"],
            sync_across_tabs=False
        )

        assert auto_save.storage_key == "custom_test"
        assert auto_save.save_interval == 5000
        assert auto_save.excluded_components == ["secret"]
        assert auto_save.sync_across_tabs == False

    def test_auto_save_state_hook(self):
        """Test auto_save_state_hook function"""
        component = auto_save_state_hook(debug=True)

        assert isinstance(component, html.Div)
        assert component.id == "auto-save-hook-container"
        assert component.style == {"display": "none"}
        assert len(component.children) >= 1


class TestAppIntegration:
    """Test app integration scenarios"""

    def test_app_layout_with_hook(self):
        """Test app layout with hook integration"""
        app = Dash(__name__)

        app.layout = html.Div([
            auto_save_state_hook(),
            dcc.Input(id="test-input", type="text"),
            html.Div(id="output")
        ])

        # Should not raise an exception
        assert app.layout is not None
        assert len(app.layout.children) == 3

    def test_app_with_enable_auto_save(self):
        """Test app with enable_auto_save"""
        app = Dash(__name__)

        app.layout = html.Div([
            dcc.Input(id="test-input", type="text"),
            html.Div(id="output")
        ])

        # Enable auto-save
        auto_save = enable_auto_save(app)

        assert isinstance(auto_save, AutoSaveState)
        assert app in auto_save._registered_apps

    def test_multiple_apps(self):
        """Test with multiple apps"""
        app1 = Dash(__name__)
        app2 = Dash(__name__)

        auto_save1 = enable_auto_save(app1, storage_key="app1_state")
        auto_save2 = enable_auto_save(app2, storage_key="app2_state")

        assert auto_save1.storage_key == "app1_state"
        assert auto_save2.storage_key == "app2_state"
        assert app1 in auto_save1._registered_apps
        assert app2 in auto_save2._registered_apps
        assert app1 not in auto_save2._registered_apps
        assert app2 not in auto_save1._registered_apps


class TestSecurityFeatures:
    """Test security-related features"""

    def test_excluded_components_in_code(self):
        """Test that excluded components appear in client-side code"""
        excluded = ["password", "secret-token"]
        auto_save = AutoSaveState(excluded_components=excluded)
        code = auto_save.get_client_side_callback_code()

        assert "password" in code
        assert "secret-token" in code

    def test_empty_excluded_components(self):
        """Test with empty excluded components list"""
        auto_save = AutoSaveState(excluded_components=[])
        code = auto_save.get_client_side_callback_code()

        assert "[]" in code  # Empty array should be in code

    def test_sync_disabled_in_code(self):
        """Test sync_across_tabs disabled in client code"""
        auto_save = AutoSaveState(sync_across_tabs=False)
        code = auto_save.get_client_side_callback_code()

        assert "false" in code.lower()  # Should contain false value


if __name__ == "__main__":
    pytest.main([__file__])