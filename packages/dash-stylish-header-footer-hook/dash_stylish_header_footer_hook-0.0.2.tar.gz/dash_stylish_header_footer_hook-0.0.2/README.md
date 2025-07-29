# Dash Hooks Demo

A stylish header and footer component for Dash applications using Dash Hooks.

## Installation

```bash
pip install dash-stylish-header-footer-hook
```

## Usage

```python
from dash import Dash
import dash_stylish_header_footer_hook  

# Register the header with custom title
dash_stylish_header_footer_hook.add_header(
    title="My Dash App",
    gradient="linear-gradient(90deg, black, red)"
)
dash_stylish_header_footer_hook.add_footer_hook(text="©2025 My Dash App",
    background="black", color="magenta", padding="20px 40px")


app = Dash(__name__)
# Rest of your app code...
```

## Example

Run the included example:

```bash
python example.py
```
