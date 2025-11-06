#!/usr/bin/env python3
"""
Test script for hatching functionality
"""

from models import BuildStep

def test_square_hatching():
    """Test hatching for a square with multiplier"""
    print("Testing square hatching with multiplier...")
    spot_size = 100.0  # 100 microns
    step = BuildStep(
        shape_type="square",
        dimensions={"size": 10.0},
        hatching_enabled=True,
        hatch_spacing_multiplier=1.0,  # 1x spot size
        hatch_angle=0.0,
        hatch_pattern="linear"
    )

    lines = step.generate_hatch_lines(spot_size)
    print(f"  Spot size: {spot_size} μm = {spot_size/1000:.3f} mm")
    print(f"  Multiplier: {step.hatch_spacing_multiplier}x")
    print(f"  Calculated spacing: {step.calculate_hatch_spacing(spot_size):.3f} mm")
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
        hatch_spacing_multiplier=2.0,
        hatch_angle=45.0,
        hatch_pattern="linear"
    )

    text = step.to_list_item_text()
    print(f"  List item text: {text}")
    print()

def test_multiplier_effect():
    """Test that different multipliers produce different spacing"""
    print("Testing multiplier effect on hatch line count...")
    spot_size = 100.0  # 100 microns
    shape = BuildStep(
        shape_type="square",
        dimensions={"size": 10.0},
        hatching_enabled=True,
        hatch_angle=0.0,
        hatch_pattern="linear"
    )

    for multiplier in [0.5, 1.0, 2.0]:
        shape.hatch_spacing_multiplier = multiplier
        lines = shape.generate_hatch_lines(spot_size)
        spacing_mm = shape.calculate_hatch_spacing(spot_size)
        print(f"  Multiplier {multiplier}x: spacing = {spacing_mm:.3f} mm, lines = {len(lines)}")
    print()

def test_different_spot_sizes():
    """Test that different spot sizes affect calculated spacing"""
    print("Testing different spot sizes...")
    multiplier = 1.0
    step = BuildStep(
        shape_type="circle",
        dimensions={"diameter": 5.0},
        hatching_enabled=True,
        hatch_spacing_multiplier=multiplier,
        hatch_angle=0.0,
        hatch_pattern="linear"
    )

    for spot_size in [50.0, 100.0, 200.0]:
        spacing_mm = step.calculate_hatch_spacing(spot_size)
        lines = step.generate_hatch_lines(spot_size)
        print(f"  Spot size {spot_size:.0f} μm: spacing = {spacing_mm:.3f} mm, lines = {len(lines)}")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("Hatching Functionality Tests with Multiplier")
    print("=" * 60)
    print()

    test_square_hatching()
    test_circle_hatching()
    test_rectangle_crosshatch()
    test_ellipse_hatching()
    test_disabled_hatching()
    test_list_item_text()
    test_multiplier_effect()
    test_different_spot_sizes()

    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)
