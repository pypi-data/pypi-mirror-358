# RustyTags IntelliSense & Autocomplete Guide

This guide shows you how to get the best IDE experience with RustyTags.

## ✅ What You Get With IntelliSense

### 1. **Tag Autocomplete**
When you type `from rusty_tags import `, you'll see all available tags:

```python
from rusty_tags import (
    Div,      # ← Autocomplete shows all HTML tags
    P,        # ← With descriptions: "Defines a paragraph"
    A,        # ← "Defines a hyperlink"
    Button,   # ← "Defines a clickable button"
    # ... all other tags
)
```

### 2. **Function Signatures**
When you type `Div(`, IDE shows:
```
Div(*children: Child, **kwargs: AttributeValue) -> HtmlString
```

### 3. **Type Hints for Children**
Children can be:
- `str` - text content
- `int`, `float`, `bool` - auto-converted to strings  
- `HtmlString` - other RustyTags elements
- `Any` - objects with `__html__()`, `_repr_html_()`, or `render()` methods

### 4. **Attribute Type Hints**
Attributes (`**kwargs`) can be:
- `str` - string values
- `int`, `float` - numbers (auto-converted)
- `bool` - booleans (true/false)

### 5. **Docstring Tooltips**
Hover over any tag to see its purpose:
- `Div` → "Defines a division or section"
- `Script` → "Defines a client-side script"
- `CustomTag` → "Creates a custom HTML tag with any tag name"

## 🎯 IDE Setup Tips

### VS Code (Recommended)
1. Install Python extension
2. Install Pylance for advanced type checking
3. Your `settings.json` should include:
```json
{
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.autoImportCompletions": true,
    "python.analysis.completeFunctionParens": true
}
```

### PyCharm
- Type checking works out of the box
- Enable "Type checking" in Python settings
- Use "Quick Documentation" (Ctrl+Q) to see docstrings

## 📝 Usage Examples

### Basic Autocomplete
```python
from rusty_tags import Div, P, A

# Type 'Div(' and see parameter hints
content = Div(
    P("Hello"),           # ← Child element
    cls="container",      # ← Common attributes show up
    id="main",           # ← Type hints guide you
    data_test="value"    # ← data-* attributes work
)
```

### Advanced Type Safety
```python
from rusty_tags import Button, Input, Form

# Type checking helps catch errors
form = Form(
    Input(type="text", name="username"),     # ← Proper string values
    Button("Submit", disabled=True),         # ← Boolean values work
    action="/submit",                        # ← Common attributes
    method="POST"                           # ← Case sensitive strings
)
```

### Custom Tags
```python
from rusty_tags import CustomTag

# Even custom tags get type hints
widget = CustomTag(
    "my-widget",              # ← tag_name parameter
    "Content here",           # ← children
    data_value=123,           # ← attributes with any name
    custom_attr="test"
)
```

## 🔍 Type Checking Benefits

With proper type hints, you get:

1. **Error Detection**: Catch mistakes before runtime
2. **Better Refactoring**: IDE can safely rename and move code
3. **Documentation**: Self-documenting code with clear types
4. **Faster Development**: Less time looking up API docs

## 🚀 Advanced Features

### Method Chaining Support
```python
# Type hints preserve return types through chains
html = Div("content").render()  # ← Returns str, not HtmlString
```

### Framework Integration
```python
# Objects with HTML methods work seamlessly
class MyComponent:
    def __html__(self):
        return "<custom>content</custom>"

# This gets proper type checking
content = Div(MyComponent())  # ← Accepts Any with __html__
```

## 🛠 Development Workflow

1. **Import with autocomplete**: `from rusty_tags import `
2. **Write with type hints**: Let IDE guide attribute names
3. **Validate with type checker**: Catch errors early
4. **Debug with tooltips**: Hover for documentation

## 📦 Files That Enable This

- `rusty_tags/__init__.py` - Exports all functions
- `rusty_tags/__init__.pyi` - Type stubs for IDE
- `pyproject.toml` - mypy/pyright configuration

This gives you a **world-class IDE experience** for HTML generation! 🎉