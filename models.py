"""
Data models for OBP Yeah U Know Me application
"""

from dataclasses import dataclass
from typing import Optional


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

    def to_list_item_text(self) -> str:
        """Format as list item text"""
        offset_str = f"@({self.x_offset:.1f},{self.y_offset:.1f})" if (self.x_offset != 0 or self.y_offset != 0) else "@(0,0)"
        layer_str = f"Layer {self.starting_layer}" if self.starting_layer > 0 else ""

        base_text = f"{self.shape_type.capitalize()} | {self.format_dimensions()} | {self.repetitions} Reps | {offset_str}"
        if layer_str:
            base_text += f" | {layer_str}"
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
