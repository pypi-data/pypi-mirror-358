#!/usr/bin/env python3
"""
Test script to demonstrate IntelliSense and autocomplete features of RustyTags
"""

# Import RustyTags - this should now show all available tags in autocomplete
from rusty_tags import (
    Div, P, A, Html, Script, CustomTag,  # Common tags
    H1, H2, H3, Button, Input, Form,     # More tags
    HtmlString, Tag                      # Core classes
)

def demo_basic_usage():
    """Basic HTML generation with type hints and autocomplete"""
    
    # Simple div with paragraph - IDE should show autocomplete for cls, id, etc.
    content = Div(
        P("Hello World", cls="greeting"),  # cls should autocomplete
        A("Click here", href="https://example.com", target="_blank"),  # href, target should autocomplete
        id="main-content",  # id should autocomplete
        cls="container"     # cls should autocomplete
    )
    
    print("Basic content:")
    print(content)
    print()

def demo_form_elements():
    """Form elements with proper type hints"""
    
    # Form with inputs - IDE should show specific attributes for each element
    form = Form(
        Input(type="text", name="username", placeholder="Enter username"),  # type, name, placeholder should autocomplete
        Input(type="password", name="password", placeholder="Enter password"),
        Button("Submit", type="submit", onclick="handleSubmit()"),  # onclick should autocomplete
        action="/login",  # action should autocomplete
        method="post"     # method should autocomplete
    )
    
    print("Form example:")
    print(form)
    print()

def demo_complete_page():
    """Complete HTML page with head/body separation"""
    
    page = Html(
        Script("console.log('Page loaded');"),  # Goes to head automatically
        H1("Welcome to RustyTags"),
        P("A high-performance HTML generation library."),
        Div(
            P("Features:", cls="intro"),
            Button("Get Started", cls="btn btn-primary"),
            cls="hero-section"
        ),
        lang="en",  # HTML attributes
        data_theme="dark"  # data attributes should work
    )
    
    print("Complete page:")
    print(page)
    print()

def demo_custom_tags():
    """Custom tags and advanced features"""
    
    # Custom web components
    custom = CustomTag(
        "my-component", 
        "Custom content here",
        data_value="123",
        custom_attr="test"
    )
    
    print("Custom tag:")
    print(custom)
    print()

def demo_type_checking():
    """Demonstrate type checking capabilities"""
    
    # These should all work with proper type conversion
    content = Div(
        P("String content"),
        P(42),           # Integer
        P(3.14),         # Float  
        P(True),         # Boolean
        P(False),        # Boolean
        cls="mixed-types"
    )
    
    print("Mixed types:")
    print(content)
    print()

if __name__ == "__main__":
    print("=== RustyTags IntelliSense Demo ===\n")
    
    demo_basic_usage()
    demo_form_elements() 
    demo_complete_page()
    demo_custom_tags()
    demo_type_checking()
    
    print("=== Demo Complete ===")
    print("\nTo test IntelliSense:")
    print("1. Open this file in VS Code")
    print("2. Try typing 'Div(' and see the autocomplete options")
    print("3. Try typing common attributes like 'cls=', 'id=', 'href='")
    print("4. Notice the function docstrings appear in hover tooltips")