# Dash Auto Save State

[![PyPI version](https://badge.fury.io/py/dash-auto-save-state.svg)](https://badge.fury.io/py/dash-auto-save-state)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

A Dash hook that automatically saves and restores component states to prevent data loss. Perfect for long forms, complex dashboards, and any application where users might accidentally lose their work.

## 🚀 Features

- **Automatic State Persistence**: Saves form inputs, selections, and other component states to localStorage
- **Cross-Tab Synchronization**: Optionally sync state changes across browser tabs
- **Configurable Exclusions**: Exclude sensitive components (passwords, tokens) from auto-save
- **Debounced Saving**: Efficiently saves state with configurable intervals
- **Zero Configuration**: Works out of the box with sensible defaults
- **Debug Mode**: Optional logging for development and troubleshooting
- **Lightweight**: Minimal overhead and dependencies

## 📦 Installation

```bash
pip install dash-auto-save-state
```

## 🔧 Quick Start

### Basic Usage

```python
from dash import Dash, html, dcc, Input, Output, callback
from dash_auto_save_state import enable_auto_save

app = Dash(__name__)

# Enable auto-save for the entire app
enable_auto_save(app)

app.layout = html.Div([
    html.H1("My Dashboard"),
    
    dcc.Input(
        id="user-name",
        type="text",
        placeholder="Enter your name..."
    ),
    
    dcc.Textarea(
        id="user-comments",
        placeholder="Enter your comments...",
        style={"width": "100%", "height": 100}
    ),
    
    dcc.Dropdown(
        id="user-country",
        options=[
            {"label": "USA", "value": "usa"},
            {"label": "Canada", "value": "canada"},
            {"label": "UK", "value": "uk"}
        ],
        placeholder="Select your country"
    ),
    
    html.Div(id="output")
])

@callback(
    Output("output", "children"),
    Input("user-name", "value"),
    Input("user-comments", "value"),
    Input("user-country", "value")
)
def update_output(name, comments, country):
    return f"Name: {name}, Comments: {comments}, Country: {country}"

if __name__ == "__main__":
    app.run(debug=True)
```

### Using Hook Function

```python
from dash import Dash, html, dcc
from dash_auto_save_state import auto_save_state_hook

app = Dash(__name__)

app.layout = html.Div([
    # Add the auto-save hook to your layout
    auto_save_state_hook(debug=True),
    
    html.H1("My Dashboard"),
    dcc.Input(id="my-input", type="text", placeholder="Type something..."),
    html.Div(id="output")
])
```

## ⚙️ Configuration Options

### Advanced Configuration

```python
from dash_auto_save_state import enable_auto_save

enable_auto_save(
    app=app,
    storage_key="my_app_state",           # Custom localStorage key
    save_interval=2000,                   # Save every 2 seconds
    excluded_components=["password-field", "secret-token"],  # Exclude sensitive fields
    sync_across_tabs=True,                # Sync between browser tabs
    debug=True                            # Enable debug logging
)
```

### Security-Focused Usage

```python
from dash_auto_save_state import secure_auto_save_hook

app.layout = html.Div([
    # Automatically excludes password fields and other sensitive components
    secure_auto_save_hook(debug=True),
    
    html.H1("Secure Form"),
    dcc.Input(id="username", type="text"),
    dcc.Input(id="password", type="password"),  # Automatically excluded
    dcc.Input(id="email", type="email"),
])
```

## 🛡️ Security Considerations

The plugin automatically excludes common sensitive field patterns:
- `password`, `pwd`, `pass`
- `secret`, `token`, `key`
- `credit-card`, `ssn`, `social-security`

You can also manually specify additional excluded components:

```python
enable_auto_save(
    app,
    excluded_components=[
        "api-key-input",
        "bank-account-field",
        "personal-id-number"
    ]
)
```

## 📊 Supported Components

The plugin automatically detects and saves state for:

- **Text Inputs**: `dcc.Input` (text, email, number, etc.)
- **Text Areas**: `dcc.Textarea`
- **Dropdowns**: `dcc.Dropdown` (single and multi-select)
- **Checkboxes**: `dcc.Checklist`
- **Radio Buttons**: `dcc.RadioItems`
- **Sliders**: `dcc.Slider`, `dcc.RangeSlider`
- **Date Pickers**: `dcc.DatePickerSingle`, `dcc.DatePickerRange`

## 🔧 API Reference

### `enable_auto_save(app, **kwargs)`

Enable auto-save functionality for a Dash app.

**Parameters:**
- `app` (dash.Dash, optional): The Dash app instance
- `storage_key` (str): Key for localStorage (default: "dash_auto_save_state")
- `save_interval` (int): Debounce interval in milliseconds (default: 1000)
- `excluded_components` (list): Component IDs to exclude from auto-save
- `sync_across_tabs` (bool): Enable cross-tab synchronization (default: True)
- `debug` (bool): Enable debug logging (default: False)

### `auto_save_state_hook(**kwargs)`

Hook function that returns auto-save components for manual layout inclusion.

### `secure_auto_save_hook(**kwargs)`

Security-focused hook that excludes sensitive components by default.

## 🧪 Testing

Run tests with:

```bash
pip install -e ".[test]"
pytest
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the [Plotly Dash](https://dash.plotly.com/) community
- Inspired by the need for better user experience in data applications
- Thanks to all contributors and users providing feedback

## 🔗 Links

- [PyPI Package]()
- [GitHub Repository](https://github.com/Feanor1992/dash-auto-save-state)


---

**Made with ❤️ for the Plotly community**