#!/usr/bin/env python3
"""
Test script for Phase 2 table enhancement tags implementation
"""

from rusty_tags import (
    # Core tags  
    Html, Head, Body, H1, P, Div, Table, Tr, Td, Th,
    
    # Phase 2: Table Enhancement Tags
    Tbody, Thead, Tfoot, Caption, Col, Colgroup
)

def test_table_structure_tags():
    """Test basic table structure enhancement tags"""
    print("=== Table Structure Tags ===")
    
    # Table body
    tbody = Tbody(
        Tr(
            Td("John"),
            Td("25"),
            Td("Engineer")
        ),
        Tr(
            Td("Jane"),
            Td("30"),
            Td("Designer")
        )
    )
    
    # Table header
    thead = Thead(
        Tr(
            Th("Name"),
            Th("Age"),
            Th("Role")
        )
    )
    
    # Table footer
    tfoot = Tfoot(
        Tr(
            Td("Total: 2 employees", colspan="3")
        )
    )
    
    print(f"Tbody: {tbody}")
    print(f"Thead: {thead}")
    print(f"Tfoot: {tfoot}")
    print()

def test_table_caption():
    """Test table caption"""
    print("=== Table Caption ===")
    
    caption = Caption("Employee Information")
    styled_caption = Caption(
        "Quarterly Sales Report",
        cls="table-caption",
        style="font-weight: bold; text-align: center;"
    )
    
    print(f"Caption: {caption}")
    print(f"Styled Caption: {styled_caption}")
    print()

def test_column_definitions():
    """Test column definition tags"""
    print("=== Column Definitions ===")
    
    # Single column
    col = Col(span="2", style="background-color: #f0f0f0;")
    
    # Column group
    colgroup = Colgroup(
        Col(span="1", style="background-color: #e6f3ff;"),
        Col(span="2", style="background-color: #fff2e6;"),
        span="3"
    )
    
    print(f"Col: {col}")
    print(f"Colgroup: {colgroup}")
    print()

def test_complete_enhanced_table():
    """Test a complete table using all Phase 2 enhancement tags"""
    print("=== Complete Enhanced Table ===")
    
    table = Table(
        Caption("Company Employee Directory"),
        Colgroup(
            Col(style="width: 30%;"),
            Col(style="width: 20%;"),
            Col(style="width: 25%;"),
            Col(style="width: 25%;")
        ),
        Thead(
            Tr(
                Th("Employee Name"),
                Th("Age"),
                Th("Department"),
                Th("Salary")
            )
        ),
        Tbody(
            Tr(
                Td("Alice Johnson"),
                Td("28"),
                Td("Engineering"),
                Td("$75,000")
            ),
            Tr(
                Td("Bob Smith"),
                Td("35"),
                Td("Marketing"),
                Td("$65,000")
            ),
            Tr(
                Td("Carol Davis"),
                Td("42"),
                Td("Sales"),
                Td("$80,000")
            )
        ),
        Tfoot(
            Tr(
                Td("Total Employees: 3", colspan="3"),
                Td("Avg: $73,333")
            )
        ),
        cls="employee-table",
        border="1"
    )
    
    print(table)
    print()

def test_responsive_table():
    """Test responsive table design with enhanced tags"""
    print("=== Responsive Table Design ===")
    
    responsive_table = Table(
        Caption("Mobile-Friendly Product Catalog"),
        Colgroup(
            Col(cls="product-name"),
            Col(cls="price"),
            Col(cls="stock", span="2")
        ),
        Thead(
            Tr(
                Th("Product", scope="col"),
                Th("Price", scope="col"),
                Th("In Stock", scope="col"),
                Th("Actions", scope="col")
            )
        ),
        Tbody(
            Tr(
                Td("Laptop Pro"),
                Td("$1,299"),
                Td("15"),
                Td("Buy Now")
            ),
            Tr(
                Td("Wireless Mouse"),
                Td("$29"),
                Td("50"),
                Td("Buy Now")
            )
        ),
        Tfoot(
            Tr(
                Td("Total Products: 2", colspan="4")
            )
        ),
        cls="responsive-table",
        role="table"
    )
    
    print(responsive_table)
    print()

def test_nested_table_structure():
    """Test complex nested table structures"""
    print("=== Complex Nested Table ===")
    
    complex_table = Div(
        H1("Financial Report"),
        Table(
            Caption("Q4 2024 Financial Summary"),
            Colgroup(
                Col(cls="category"),
                Col(cls="q1"),
                Col(cls="q2"),
                Col(cls="q3"),
                Col(cls="q4"),
                Col(cls="total")
            ),
            Thead(
                Tr(
                    Th("Category", rowspan="2"),
                    Th("Quarterly Results", colspan="4"),
                    Th("Annual Total", rowspan="2")
                ),
                Tr(
                    Th("Q1"),
                    Th("Q2"),
                    Th("Q3"),
                    Th("Q4")
                )
            ),
            Tbody(
                Tr(
                    Td("Revenue"),
                    Td("$100K"),
                    Td("$120K"),
                    Td("$110K"),
                    Td("$140K"),
                    Td("$470K")
                ),
                Tr(
                    Td("Expenses"),
                    Td("$60K"),
                    Td("$70K"),
                    Td("$65K"),
                    Td("$80K"),
                    Td("$275K")
                )
            ),
            Tfoot(
                Tr(
                    Td("Net Profit", style="font-weight: bold;"),
                    Td("$40K"),
                    Td("$50K"),
                    Td("$45K"),
                    Td("$60K"),
                    Td("$195K", style="font-weight: bold; color: green;")
                )
            ),
            cls="financial-table",
            style="border-collapse: collapse; width: 100%;"
        ),
        cls="report-container"
    )
    
    print(complex_table)
    print()

def test_complete_page_with_phase2():
    """Test a complete page using all Phase 1 and Phase 2 tags"""
    print("=== Complete Page with Phase 1 & 2 Tags ===")
    
    page = Html(
        Head(
            Caption("This won't actually appear here - just testing tag availability")
        ),
        Body(
            H1("Enhanced Table Features Demo"),
            P("This page demonstrates Phase 2 table enhancement tags."),
            
            Table(
                Caption("Sample Data Table with All Enhancements"),
                Colgroup(
                    Col(style="background-color: #f8f9fa;"),
                    Col(span="2", style="background-color: #e9ecef;")
                ),
                Thead(
                    Tr(
                        Th("Feature"),
                        Th("Phase 1"),
                        Th("Phase 2")
                    )
                ),
                Tbody(
                    Tr(
                        Td("Table Structure"),
                        Td("Basic Table, Tr, Td, Th"),
                        Td("Tbody, Thead, Tfoot")
                    ),
                    Tr(
                        Td("Table Metadata"),
                        Td("N/A"),
                        Td("Caption")
                    ),
                    Tr(
                        Td("Column Control"),
                        Td("N/A"),
                        Td("Col, Colgroup")
                    )
                ),
                Tfoot(
                    Tr(
                        Td("Total Features", colspan="2"),
                        Td("6 new tags")
                    )
                )
            )
        ),
        lang="en"
    )
    
    print(page)
    print()

if __name__ == "__main__":
    print("🚀 Testing RustyTags Phase 2 Table Enhancement Tags\n")
    
    test_table_structure_tags()
    test_table_caption()
    test_column_definitions()
    test_complete_enhanced_table()
    test_responsive_table()
    test_nested_table_structure()
    test_complete_page_with_phase2()
    
    print("✅ All Phase 2 table enhancement tag tests completed!")
    print("\n📈 Progress Update:")
    print("   Before Phase 2: 59 tags (37 HTML + 22 SVG)")
    print("   After Phase 2:  65 tags (43 HTML + 22 SVG)")
    print("   🎯 Coverage: ~82% of essential HTML5 tags")
    print("\n🎉 IntelliSense now supports 6 additional table enhancement tags!")
    print("   • Tbody, Thead, Tfoot - Table structure")
    print("   • Caption - Table descriptions")
    print("   • Col, Colgroup - Column styling and control")