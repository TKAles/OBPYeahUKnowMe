"""
Data models for OBP Yeah U Know Me application
"""

from dataclasses import dataclass
from typing import Optional, List, Tuple
import math


@dataclass
class RecoaterSettings:
    """Data structure to hold recoater blade parameters"""
    advance_velocity: float = 10.0  # mm/s
    retract_velocity: float = 15.0  # mm/s
    dwell_time: float = 2.0         # seconds
    full_repeats: int = 1
    cycle_repeats: int = 1


@dataclass
class BuildStep:
    """Data structure to hold build step parameters"""
    shape_type: str = ""
    dimensions: dict = None
    repetitions: int = 1
    x_offset: float = 0.0  # mm
    y_offset: float = 0.0  # mm
    starting_layer: int = 0  # Layer number to start building (0-based)

    # Hatching parameters
    hatching_enabled: bool = False
    hatch_spacing: float = 0.1  # mm - distance between hatch lines (calculated from multiplier * spot_size)
    hatch_spacing_multiplier: float = 1.0  # multiplier for beam spot size (1.0 = spacing equals spot size)
    hatch_angle: float = 0.0  # degrees - rotation of hatch pattern
    hatch_pattern: str = "linear"  # "linear" or "crosshatch"

    def __post_init__(self):
        if self.dimensions is None:
            self.dimensions = {}

    def format_dimensions(self) -> str:
        """Format dimensions for display"""
        if self.shape_type == "square":
            return f"{self.dimensions.get('size', 0)}x{self.dimensions.get('size', 0)}mm"
        elif self.shape_type == "rectangle":
            return f"{self.dimensions.get('width', 0)}x{self.dimensions.get('length', 0)}mm"
        elif self.shape_type == "circle":
            return f"Ø{self.dimensions.get('diameter', 0)}mm"
        elif self.shape_type == "ellipse":
            return f"{self.dimensions.get('width', 0)}x{self.dimensions.get('length', 0)}mm ellipse"
        return ""

    def calculate_total_height(self, layer_height: float) -> float:
        """Calculate total build height from repetitions and layer height"""
        return self.repetitions * layer_height

    def calculate_hatch_spacing(self, spot_size_microns: float) -> float:
        """
        Calculate actual hatch spacing from spot size and multiplier.
        Args:
            spot_size_microns: Beam spot size in microns
        Returns:
            Hatch spacing in mm
        """
        spot_size_mm = spot_size_microns / 1000.0  # Convert microns to mm
        return spot_size_mm * self.hatch_spacing_multiplier

    def to_list_item_text(self) -> str:
        """Format as list item text"""
        offset_str = f"@({self.x_offset:.1f},{self.y_offset:.1f})" if (self.x_offset != 0 or self.y_offset != 0) else "@(0,0)"
        layer_str = f"Layer {self.starting_layer}" if self.starting_layer > 0 else ""

        base_text = f"{self.shape_type.capitalize()} | {self.format_dimensions()} | {self.repetitions} Reps | {offset_str}"
        if layer_str:
            base_text += f" | {layer_str}"
        if self.hatching_enabled:
            base_text += f" | Hatch: {self.hatch_spacing_multiplier}x@{self.hatch_angle}°"
        return base_text

    @classmethod
    def from_list_item_text(cls, text: str) -> 'BuildStep':
        """Parse BuildStep from list item text"""
        try:
            parts = text.split(" | ")
            if len(parts) < 4:
                raise ValueError("Invalid format")

            shape_type = parts[0].lower()
            dimensions_str = parts[1]
            repetitions = int(parts[2].split()[0])

            # Parse offset from format "@(x,y)"
            offset_str = parts[3]
            x_offset = 0.0
            y_offset = 0.0
            if offset_str.startswith("@(") and offset_str.endswith(")"):
                coords = offset_str[2:-1].split(",")
                if len(coords) == 2:
                    x_offset = float(coords[0])
                    y_offset = float(coords[1])

            # Parse starting layer if present
            starting_layer = 0
            if len(parts) >= 5 and parts[4].startswith("Layer "):
                starting_layer = int(parts[4].split()[1])

            # Parse dimensions based on shape type
            dimensions = {}
            if shape_type == "square":
                # Format: "10.0x10.0mm"
                dims = dimensions_str.replace("mm", "").split("x")
                if len(dims) == 2:
                    dimensions = {"size": float(dims[0])}
            elif shape_type == "rectangle":
                # Format: "15.0x20.0mm"
                dims = dimensions_str.replace("mm", "").split("x")
                if len(dims) == 2:
                    dimensions = {"width": float(dims[0]), "length": float(dims[1])}
            elif shape_type == "circle":
                # Format: "Ø25.0mm"
                dims = dimensions_str.replace("Ø", "").replace("mm", "")
                if dims:
                    dimensions = {"diameter": float(dims)}
            elif shape_type == "ellipse":
                # Format: "12.0x18.0mm ellipse"
                dims = dimensions_str.replace("mm ellipse", "").split("x")
                if len(dims) == 2:
                    dimensions = {"width": float(dims[0]), "length": float(dims[1])}

            return cls(
                shape_type=shape_type,
                dimensions=dimensions,
                repetitions=repetitions,
                x_offset=x_offset,
                y_offset=y_offset,
                starting_layer=starting_layer
            )

        except (ValueError, IndexError):
            # Return default if parsing fails
            return cls()

    def generate_hatch_lines(self, spot_size_microns: float = 100.0) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """
        Generate hatch lines as (start_point, end_point) pairs.
        Args:
            spot_size_microns: Beam spot size in microns (default 100)
        Returns:
            List of tuples: [((x1, y1), (x2, y2)), ...]
            Points are in absolute coordinates including offsets.
        """
        if not self.hatching_enabled:
            return []

        # Calculate actual hatch spacing from spot size and multiplier
        actual_spacing = self.calculate_hatch_spacing(spot_size_microns)

        # Store the calculated spacing for use in generation methods
        self._actual_hatch_spacing = actual_spacing

        # Generate primary hatch lines
        lines = self._generate_hatch_lines_at_angle(self.hatch_angle)

        # Add secondary lines for crosshatch pattern
        if self.hatch_pattern == "crosshatch":
            secondary_angle = self.hatch_angle + 90.0
            secondary_lines = self._generate_hatch_lines_at_angle(secondary_angle)
            lines.extend(secondary_lines)

        return lines

    def _generate_hatch_lines_at_angle(self, angle_deg: float) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """
        Generate hatch lines at a specific angle for the shape.
        Returns list of ((x1, y1), (x2, y2)) tuples in absolute coordinates.
        """
        if self.shape_type == "square":
            return self._generate_rectangle_hatches(
                self.dimensions.get('size', 0),
                self.dimensions.get('size', 0),
                angle_deg
            )
        elif self.shape_type == "rectangle":
            return self._generate_rectangle_hatches(
                self.dimensions.get('width', 0),
                self.dimensions.get('length', 0),
                angle_deg
            )
        elif self.shape_type == "circle":
            return self._generate_circle_hatches(
                self.dimensions.get('diameter', 0),
                angle_deg
            )
        elif self.shape_type == "ellipse":
            return self._generate_ellipse_hatches(
                self.dimensions.get('width', 0),
                self.dimensions.get('length', 0),
                angle_deg
            )
        return []

    def _generate_rectangle_hatches(self, width: float, height: float, angle_deg: float) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """Generate hatch lines for a rectangle at a given angle"""
        lines = []
        spacing = getattr(self, '_actual_hatch_spacing', self.hatch_spacing)
        if width <= 0 or height <= 0 or spacing <= 0:
            return lines

        angle_rad = math.radians(angle_deg)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        # Calculate bounding box diagonal to ensure full coverage
        diagonal = math.sqrt(width**2 + height**2)

        # Generate parallel lines perpendicular to the hatch angle
        # Start from beyond the shape and sweep across
        num_lines = int(diagonal / spacing) + 2
        start_offset = -diagonal / 2

        for i in range(num_lines):
            # Distance along perpendicular to hatch direction
            offset = start_offset + i * spacing

            # Line passes through point at offset distance from center
            # perpendicular to hatch direction
            px = -offset * sin_a
            py = offset * cos_a

            # Extend line far in both directions along hatch angle
            t_max = diagonal
            p1 = (px - t_max * cos_a, py - t_max * sin_a)
            p2 = (px + t_max * cos_a, py + t_max * sin_a)

            # Clip line to rectangle bounds
            clipped = self._clip_line_to_rectangle(p1, p2, width, height)
            if clipped:
                # Apply offset and convert to absolute coordinates
                (x1, y1), (x2, y2) = clipped
                lines.append((
                    (x1 + self.x_offset, y1 + self.y_offset),
                    (x2 + self.x_offset, y2 + self.y_offset)
                ))

        return lines

    def _generate_circle_hatches(self, diameter: float, angle_deg: float) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """Generate hatch lines for a circle at a given angle"""
        lines = []
        spacing = getattr(self, '_actual_hatch_spacing', self.hatch_spacing)
        if diameter <= 0 or spacing <= 0:
            return lines

        radius = diameter / 2
        angle_rad = math.radians(angle_deg)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        # Generate parallel lines
        num_lines = int(diameter / spacing) + 2
        start_offset = -radius - spacing

        for i in range(num_lines):
            # Perpendicular distance from center
            offset = start_offset + i * spacing

            # Skip if line doesn't intersect circle
            if abs(offset) >= radius:
                continue

            # Calculate chord length
            chord_half_length = math.sqrt(radius**2 - offset**2)

            # Center point of chord
            px = -offset * sin_a
            py = offset * cos_a

            # Endpoints of chord
            x1 = px - chord_half_length * cos_a
            y1 = py - chord_half_length * sin_a
            x2 = px + chord_half_length * cos_a
            y2 = py + chord_half_length * sin_a

            # Apply offset and convert to absolute coordinates
            lines.append((
                (x1 + self.x_offset, y1 + self.y_offset),
                (x2 + self.x_offset, y2 + self.y_offset)
            ))

        return lines

    def _generate_ellipse_hatches(self, width: float, height: float, angle_deg: float) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """Generate hatch lines for an ellipse at a given angle"""
        lines = []
        spacing = getattr(self, '_actual_hatch_spacing', self.hatch_spacing)
        if width <= 0 or height <= 0 or spacing <= 0:
            return lines

        a = width / 2  # Semi-major axis (assuming width is along x)
        b = height / 2  # Semi-minor axis (assuming height is along y)

        angle_rad = math.radians(angle_deg)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        # Use bounding box diagonal for range
        diagonal = math.sqrt(width**2 + height**2)
        num_lines = int(diagonal / spacing) + 2
        start_offset = -diagonal / 2

        for i in range(num_lines):
            offset = start_offset + i * spacing

            # For an ellipse, we need to find intersection of line with ellipse
            # Line: perpendicular distance 'offset' from center, direction (cos_a, sin_a)
            # Parametric: (x, y) = (-offset*sin_a, offset*cos_a) + t*(cos_a, sin_a)

            # Substitute into ellipse equation: (x/a)^2 + (y/b)^2 = 1
            px = -offset * sin_a
            py = offset * cos_a

            # Solve quadratic equation for t
            A = (cos_a/a)**2 + (sin_a/b)**2
            B = 2 * (px*cos_a/a**2 + py*sin_a/b**2)
            C = (px/a)**2 + (py/b)**2 - 1

            discriminant = B**2 - 4*A*C
            if discriminant < 0:
                continue  # No intersection

            sqrt_disc = math.sqrt(discriminant)
            t1 = (-B - sqrt_disc) / (2*A)
            t2 = (-B + sqrt_disc) / (2*A)

            # Calculate intersection points
            x1 = px + t1 * cos_a
            y1 = py + t1 * sin_a
            x2 = px + t2 * cos_a
            y2 = py + t2 * sin_a

            # Apply offset and convert to absolute coordinates
            lines.append((
                (x1 + self.x_offset, y1 + self.y_offset),
                (x2 + self.x_offset, y2 + self.y_offset)
            ))

        return lines

    def _clip_line_to_rectangle(self, p1: Tuple[float, float], p2: Tuple[float, float],
                                 width: float, height: float) -> Optional[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """
        Clip a line segment to a rectangle centered at origin using Cohen-Sutherland algorithm.
        Returns clipped line as ((x1, y1), (x2, y2)) or None if completely outside.
        """
        # Rectangle bounds (centered at origin)
        x_min, x_max = -width/2, width/2
        y_min, y_max = -height/2, height/2

        x1, y1 = p1
        x2, y2 = p2

        # Cohen-Sutherland outcodes
        INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8

        def compute_outcode(x, y):
            code = INSIDE
            if x < x_min:
                code |= LEFT
            elif x > x_max:
                code |= RIGHT
            if y < y_min:
                code |= BOTTOM
            elif y > y_max:
                code |= TOP
            return code

        outcode1 = compute_outcode(x1, y1)
        outcode2 = compute_outcode(x2, y2)

        while True:
            # Both points inside
            if outcode1 == 0 and outcode2 == 0:
                return ((x1, y1), (x2, y2))

            # Both points outside same region
            if (outcode1 & outcode2) != 0:
                return None

            # At least one point outside, clip it
            outcode = outcode1 if outcode1 != 0 else outcode2

            # Find intersection point
            if outcode & TOP:
                x = x1 + (x2 - x1) * (y_max - y1) / (y2 - y1)
                y = y_max
            elif outcode & BOTTOM:
                x = x1 + (x2 - x1) * (y_min - y1) / (y2 - y1)
                y = y_min
            elif outcode & RIGHT:
                y = y1 + (y2 - y1) * (x_max - x1) / (x2 - x1)
                x = x_max
            elif outcode & LEFT:
                y = y1 + (y2 - y1) * (x_min - x1) / (x2 - x1)
                x = x_min

            # Update point and outcode
            if outcode == outcode1:
                x1, y1 = x, y
                outcode1 = compute_outcode(x1, y1)
            else:
                x2, y2 = x, y
                outcode2 = compute_outcode(x2, y2)
