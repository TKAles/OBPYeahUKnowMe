#!/usr/bin/env python3
"""
Test script for hatching functionality
"""

from models import BuildStep

def test_square_hatching():
    """Test hatching for a square"""
    print("Testing square hatching...")
    step = BuildStep(
        shape_type="square",
        dimensions={"size": 10.0},
        hatching_enabled=True,
        hatch_spacing=1.0,
        hatch_angle=0.0,
        hatch_pattern="linear"
    )

    lines = step.generate_hatch_lines()
    print(f"  Generated {len(lines)} hatch lines")
    if lines:
        print(f"  First line: {lines[0]}")
        print(f"  Last line: {lines[-1]}")
    print()

def test_circle_hatching():
    """Test hatching for a circle"""
    print("Testing circle hatching...")
    step = BuildStep(
        shape_type="circle",
        dimensions={"diameter": 10.0},
        hatching_enabled=True,
        hatch_spacing=1.0,
        hatch_angle=45.0,
        hatch_pattern="linear"
    )

    lines = step.generate_hatch_lines()
    print(f"  Generated {len(lines)} hatch lines")
    if lines:
        print(f"  First line: {lines[0]}")
        print(f"  Last line: {lines[-1]}")
    print()

def test_rectangle_crosshatch():
    """Test crosshatch pattern for a rectangle"""
    print("Testing rectangle crosshatch...")
    step = BuildStep(
        shape_type="rectangle",
        dimensions={"width": 15.0, "length": 20.0},
        hatching_enabled=True,
        hatch_spacing=2.0,
        hatch_angle=0.0,
        hatch_pattern="crosshatch",
        x_offset=10.0,
        y_offset=5.0
    )

    lines = step.generate_hatch_lines()
    print(f"  Generated {len(lines)} hatch lines")
    if lines:
        print(f"  First line: {lines[0]}")
        print(f"  Last line: {lines[-1]}")
    print()

def test_ellipse_hatching():
    """Test hatching for an ellipse"""
    print("Testing ellipse hatching...")
    step = BuildStep(
        shape_type="ellipse",
        dimensions={"width": 12.0, "length": 18.0},
        hatching_enabled=True,
        hatch_spacing=1.5,
        hatch_angle=30.0,
        hatch_pattern="linear"
    )

    lines = step.generate_hatch_lines()
    print(f"  Generated {len(lines)} hatch lines")
    if lines:
        print(f"  First line: {lines[0]}")
        print(f"  Last line: {lines[-1]}")
    print()

def test_disabled_hatching():
    """Test that disabled hatching returns empty list"""
    print("Testing disabled hatching...")
    step = BuildStep(
        shape_type="square",
        dimensions={"size": 10.0},
        hatching_enabled=False
    )

    lines = step.generate_hatch_lines()
    print(f"  Generated {len(lines)} hatch lines (should be 0)")
    print()

def test_list_item_text():
    """Test that hatching info is shown in list item text"""
    print("Testing list item text with hatching...")
    step = BuildStep(
        shape_type="square",
        dimensions={"size": 10.0},
        repetitions=5,
        x_offset=2.5,
        y_offset=3.0,
        hatching_enabled=True,
        hatch_spacing=0.5,
        hatch_angle=45.0,
        hatch_pattern="linear"
    )

    text = step.to_list_item_text()
    print(f"  List item text: {text}")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("Hatching Functionality Tests")
    print("=" * 60)
    print()

    test_square_hatching()
    test_circle_hatching()
    test_rectangle_crosshatch()
    test_ellipse_hatching()
    test_disabled_hatching()
    test_list_item_text()

    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)
