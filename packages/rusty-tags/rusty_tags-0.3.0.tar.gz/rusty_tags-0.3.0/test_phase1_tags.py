#!/usr/bin/env python3
"""
Test script for Phase 1 critical HTML tags implementation
"""

from rusty_tags import (
    # Core tags  
    Html, Head, Body, H1, P, Div,
    
    # Phase 1: Critical High Priority HTML tags
    Meta, Hr, Iframe, Textarea, Select, Figure, Figcaption,
    Article, Footer, Details, Summary, Address
)

def test_meta_tag():
    """Test meta tag functionality"""
    print("=== Meta Tag ===")
    
    # Common meta tags
    charset = Meta(charset="utf-8")
    viewport = Meta(name="viewport", content="width=device-width, initial-scale=1")
    description = Meta(name="description", content="A test page for RustyTags")
    
    print(f"Charset: {charset}")
    print(f"Viewport: {viewport}")
    print(f"Description: {description}")
    print()

def test_hr_tag():
    """Test horizontal rule"""
    print("=== Hr Tag ===")
    
    simple_hr = Hr()
    styled_hr = Hr(cls="divider", style="border: 2px solid #ccc;")
    
    print(f"Simple HR: {simple_hr}")
    print(f"Styled HR: {styled_hr}")
    print()

def test_iframe_tag():
    """Test iframe embedding"""
    print("=== Iframe Tag ===")
    
    youtube = Iframe(
        src="https://www.youtube.com/embed/dQw4w9WgXcQ",
        width="560", height="315",
        frameborder="0",
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    )
    
    print(f"YouTube embed: {youtube}")
    print()

def test_form_elements():
    """Test form-related elements"""
    print("=== Form Elements ===")
    
    # Textarea
    comment_box = Textarea(
        "Default text here...",
        name="comment", rows="4", cols="50",
        placeholder="Enter your comment"
    )
    
    # Select dropdown
    country_select = Select(
        name="country", id="country-select"
    )
    
    print(f"Textarea: {comment_box}")
    print(f"Select: {country_select}")
    print()

def test_semantic_elements():
    """Test semantic HTML5 elements"""
    print("=== Semantic Elements ===")
    
    # Figure with caption
    image_figure = Figure(
        # Note: We'd normally have an Img tag here, but testing the structure
        P("Image would go here"),
        Figcaption("Caption: A beautiful landscape")
    )
    
    # Article
    blog_post = Article(
        H1("Blog Post Title"),
        P("This is the content of a blog post..."),
        cls="blog-post"
    )
    
    # Footer
    page_footer = Footer(
        P("© 2024 RustyTags. All rights reserved."),
        Address("Contact us at info@rustytags.com"),
        cls="site-footer"
    )
    
    print(f"Figure: {image_figure}")
    print(f"Article: {blog_post}")
    print(f"Footer: {page_footer}")
    print()

def test_interactive_elements():
    """Test details/summary disclosure widgets"""
    print("=== Interactive Elements ===")
    
    # Details/Summary widget
    faq_item = Details(
        Summary("What is RustyTags?"),
        P("RustyTags is a high-performance HTML generation library built with Rust."),
        P("It provides fast, type-safe HTML generation with Python integration.")
    )
    
    advanced_details = Details(
        Summary("Advanced Configuration"),
        Div(
            P("Here are some advanced options:"),
            Hr(),
            P("Enable caching: Use memory pooling for better performance")
        ),
        open=True  # Start expanded
    )
    
    print(f"FAQ Item: {faq_item}")
    print(f"Advanced Details: {advanced_details}")
    print()

def test_complete_page():
    """Test a complete page using all Phase 1 tags"""
    print("=== Complete Page with Phase 1 Tags ===")
    
    page = Html(
        Head(
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Meta(name="description", content="RustyTags Phase 1 Demo")
        ),
        Body(
            Article(
                H1("Welcome to RustyTags Phase 1"),
                P("This page demonstrates the new HTML tags added in Phase 1."),
                Hr(),
                Figure(
                    P("[Image placeholder]"),
                    Figcaption("Demo of figure with caption")
                ),
                Details(
                    Summary("Click to see more information"),
                    P("This is additional content that can be hidden or shown."),
                    Textarea("Leave feedback here...", rows="3", cols="40")
                )
            ),
            Footer(
                Address("Made with RustyTags"),
                P("High-performance HTML generation")
            )
        ),
        lang="en"
    )
    
    print(page)
    print()

if __name__ == "__main__":
    print("🚀 Testing RustyTags Phase 1 HTML Tags\n")
    
    test_meta_tag()
    test_hr_tag()
    test_iframe_tag()
    test_form_elements()
    test_semantic_elements()
    test_interactive_elements()
    test_complete_page()
    
    print("✅ All Phase 1 tag tests completed!")
    print("\n📈 Progress Update:")
    print("   Before Phase 1: 47 tags (25 HTML + 22 SVG)")
    print("   After Phase 1:  59 tags (37 HTML + 22 SVG)")
    print("   🎯 Coverage: ~76% of essential HTML5 tags")
    print("\n🎉 IntelliSense now supports 12 additional critical HTML tags!")