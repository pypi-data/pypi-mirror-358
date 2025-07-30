#!/usr/bin/env python3
"""
Test script to demonstrate SVG functionality in RustyTags
"""

# Import both HTML and SVG tags
from rusty_tags import (
    # HTML tags
    Html, Head, Body, H1, Div,
    
    # SVG tags - now available!
    Svg, Circle, Rect, Line, Path, Text, G, Defs, LinearGradient, Stop,
    Polygon, Ellipse, Use, Symbol, Marker, ClipPath, Mask
)

def test_basic_svg():
    """Test basic SVG shapes"""
    print("=== Basic SVG Shapes ===")
    
    svg = Svg(
        Circle(cx="50", cy="50", r="40", fill="red"),
        Rect(x="10", y="10", width="30", height="30", fill="blue"),
        Line(x1="0", y1="0", x2="100", y2="100", stroke="green", stroke_width="2"),
        width="200", height="200", viewBox="0 0 200 200"
    )
    
    print(svg)
    print()

def test_svg_with_gradients():
    """Test SVG with gradients and advanced features"""
    print("=== SVG with Gradients ===")
    
    svg = Svg(
        Defs(
            LinearGradient(
                Stop(offset="0%", stop_color="red"),
                Stop(offset="100%", stop_color="blue"),
                id="gradient1"
            )
        ),
        Circle(
            cx="100", cy="100", r="80",
            fill="url(#gradient1)"
        ),
        width="200", height="200"
    )
    
    print(svg)
    print()

def test_svg_text_and_paths():
    """Test SVG text and paths"""
    print("=== SVG Text and Paths ===")
    
    svg = Svg(
        Text("Hello SVG!", x="10", y="50", font_family="Arial", font_size="16", fill="black"),
        Path(d="M 10 80 Q 95 10 180 80", stroke="orange", stroke_width="3", fill="none"),
        Polygon(points="100,10 40,198 190,78 10,78 160,198", fill="purple", opacity="0.7"),
        width="200", height="220"
    )
    
    print(svg)
    print()

def test_svg_groups_and_reuse():
    """Test SVG groups and reusable elements"""
    print("=== SVG Groups and Reuse ===")
    
    svg = Svg(
        Defs(
            G(
                Circle(cx="0", cy="0", r="10", fill="green"),
                id="dot"
            )
        ),
        G(
            Use(href="#dot", x="50", y="50"),
            Use(href="#dot", x="100", y="50"),
            Use(href="#dot", x="150", y="50"),
            transform="rotate(45 100 100)"
        ),
        width="200", height="200"
    )
    
    print(svg)
    print()

def test_complete_html_with_svg():
    """Test complete HTML page with embedded SVG"""
    print("=== Complete HTML with SVG ===")
    
    page = Html(
        Head(),
        Body(
            H1("RustyTags SVG Demo"),
            Div(
                Svg(
                    Circle(cx="50", cy="50", r="40", fill="lightblue", stroke="navy", stroke_width="2"),
                    Text("SVG", x="30", y="55", font_family="Arial", font_size="12", fill="navy"),
                    width="100", height="100"
                ),
                cls="svg-container"
            )
        ),
        lang="en"
    )
    
    print(page)
    print()

def test_advanced_svg_features():
    """Test advanced SVG features like clipping and masking"""
    print("=== Advanced SVG Features ===")
    
    svg = Svg(
        Defs(
            ClipPath(
                Circle(cx="100", cy="100", r="50"),
                id="circle-clip"
            ),
            Mask(
                Rect(x="0", y="0", width="200", height="200", fill="white"),
                Circle(cx="100", cy="100", r="30", fill="black"),
                id="hole-mask"
            )
        ),
        G(
            Rect(x="50", y="50", width="100", height="100", fill="red"),
            clip_path="url(#circle-clip)"
        ),
        Ellipse(
            cx="100", cy="100", rx="80", ry="40", 
            fill="blue", mask="url(#hole-mask)"
        ),
        width="200", height="200"
    )
    
    print(svg)
    print()

if __name__ == "__main__":
    print("🎨 RustyTags SVG Functionality Test\n")
    
    test_basic_svg()
    test_svg_with_gradients()
    test_svg_text_and_paths()
    test_svg_groups_and_reuse()
    test_complete_html_with_svg()
    test_advanced_svg_features()
    
    print("✅ All SVG tests completed!")
    print("\n📋 Available SVG tags in RustyTags:")
    print("   Svg, Circle, Rect, Line, Path, Polygon, Polyline, Ellipse")
    print("   Text, G, Defs, Use, Symbol, Marker, LinearGradient, RadialGradient")
    print("   Stop, Pattern, ClipPath, Mask, Image, ForeignObject")
    print("\n🎯 IntelliSense now supports all these SVG tags with proper type hints!")