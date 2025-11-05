"""
Main application entry point for OBP Yeah U Know Me
"""

import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMainWindow, QDialog, QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QRadioButton, QLabel, QLineEdit, QButtonGroup, QListWidgetItem, QPushButton, QComboBox, QMessageBox
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QBrush, QColor, QPen
import math
import numpy as np

# Matplotlib for 3D visualization
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    from mpl_toolkits.mplot3d import Axes3D
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Matplotlib not available - using fallback visualization")
from dataclasses import dataclass
from typing import Optional

# Simple 2D visualization using QGraphicsView - no OpenGL required


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
        return f"{self.shape_type.capitalize()} | {self.format_dimensions()} | {self.repetitions} Repetitions"

    @classmethod
    def from_list_item_text(cls, text: str) -> 'BuildStep':
        """Parse BuildStep from list item text"""
        try:
            parts = text.split(" | ")
            if len(parts) != 3:
                raise ValueError("Invalid format")

            shape_type = parts[0].lower()
            dimensions_str = parts[1]
            repetitions = int(parts[2].split()[0])

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

            return cls(shape_type=shape_type, dimensions=dimensions, repetitions=repetitions)

        except (ValueError, IndexError):
            # Return default if parsing fails
            return cls()


class ShapeSelectionPage(QWizardPage):
    """First page of wizard - select shape type"""

    def __init__(self):
        super().__init__()
        self.setTitle("Select Shape Type")
        self.setSubTitle("Choose the type of shape you want to create:")

        layout = QVBoxLayout()

        # Create radio buttons for shape selection
        self.square_radio = QRadioButton("Square")
        self.rectangle_radio = QRadioButton("Rectangle")
        self.circle_radio = QRadioButton("Circle")
        self.ellipse_radio = QRadioButton("Ellipse")

        # Group radio buttons
        self.shape_group = QButtonGroup()
        self.shape_group.addButton(self.square_radio, 0)
        self.shape_group.addButton(self.rectangle_radio, 1)
        self.shape_group.addButton(self.circle_radio, 2)
        self.shape_group.addButton(self.ellipse_radio, 3)

        # Set default selection
        self.square_radio.setChecked(True)

        # Connect signals
        self.shape_group.buttonClicked.connect(self.completeChanged.emit)

        # Add to layout
        layout.addWidget(self.square_radio)
        layout.addWidget(self.rectangle_radio)
        layout.addWidget(self.circle_radio)
        layout.addWidget(self.ellipse_radio)
        layout.addStretch()

        self.setLayout(layout)

        # Register fields for next page
        self.registerField("shape_type", self.square_radio)

    def isComplete(self):
        """Page is complete when a shape is selected"""
        return self.shape_group.checkedButton() is not None

    def get_selected_shape(self):
        """Get the selected shape type"""
        shapes = ["square", "rectangle", "circle", "ellipse"]
        checked_id = self.shape_group.checkedId()
        return shapes[checked_id] if checked_id >= 0 else "square"


class ParametersPage(QWizardPage):
    """Second page of wizard - input shape parameters"""

    def __init__(self):
        super().__init__()
        self.setTitle("Shape Parameters")
        self.setSubTitle("Enter the dimensions for your shape:")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Will be populated based on shape selection
        self.parameter_widgets = {}

    def initializePage(self):
        """Initialize page based on selected shape from previous page"""
        # Clear existing widgets
        for i in reversed(range(self.layout.count())):
            child = self.layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        self.parameter_widgets.clear()

        # Get selected shape from previous page
        shape_page = self.wizard().page(0)
        shape_type = shape_page.get_selected_shape()

        if shape_type == "square":
            self.setup_square_parameters()
        elif shape_type == "rectangle":
            self.setup_rectangle_parameters()
        elif shape_type == "circle":
            self.setup_circle_parameters()
        elif shape_type == "ellipse":
            self.setup_ellipse_parameters()

        # Add repetitions field (common to all shapes)
        self.add_repetitions_field()

    def setup_square_parameters(self):
        """Setup parameters for square"""
        self.add_parameter_field("Size", "size", "mm")

    def setup_rectangle_parameters(self):
        """Setup parameters for rectangle"""
        self.add_parameter_field("Width", "width", "mm")
        self.add_parameter_field("Length", "length", "mm")

    def setup_circle_parameters(self):
        """Setup parameters for circle"""
        self.add_parameter_field("Diameter", "diameter", "mm")

    def setup_ellipse_parameters(self):
        """Setup parameters for ellipse"""
        self.add_parameter_field("Width", "width", "mm")
        self.add_parameter_field("Length", "length", "mm")

    def add_parameter_field(self, label_text, field_name, unit):
        """Add a parameter input field"""
        h_layout = QHBoxLayout()

        label = QLabel(f"{label_text}:")
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("0.0")
        unit_label = QLabel(f"[{unit}]")

        h_layout.addWidget(label)
        h_layout.addWidget(line_edit)
        h_layout.addWidget(unit_label)

        self.layout.addLayout(h_layout)
        self.parameter_widgets[field_name] = line_edit

        # Connect to validation
        line_edit.textChanged.connect(self.completeChanged.emit)

    def add_repetitions_field(self):
        """Add repetitions field"""
        h_layout = QHBoxLayout()

        label = QLabel("Repetitions:")
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("1")
        line_edit.setText("1")  # Default value

        h_layout.addWidget(label)
        h_layout.addWidget(line_edit)
        h_layout.addStretch()

        self.layout.addLayout(h_layout)
        self.parameter_widgets["repetitions"] = line_edit

        # Connect to validation
        line_edit.textChanged.connect(self.completeChanged.emit)

    def isComplete(self):
        """Page is complete when all required fields have valid values"""
        try:
            for field_name, widget in self.parameter_widgets.items():
                text = widget.text().strip()
                if not text:
                    return False

                if field_name == "repetitions":
                    value = int(text)
                    if value < 1:
                        return False
                else:
                    value = float(text)
                    if value <= 0:
                        return False
            return True
        except (ValueError, TypeError):
            return False

    def get_parameters(self):
        """Get the entered parameters as a dictionary"""
        params = {}
        for field_name, widget in self.parameter_widgets.items():
            try:
                if field_name == "repetitions":
                    params[field_name] = int(widget.text())
                else:
                    params[field_name] = float(widget.text())
            except (ValueError, TypeError):
                params[field_name] = 0
        return params


class BuildStepWizard(QWizard):
    """Wizard for creating new build steps"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Build Step")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)

        # Add pages
        self.shape_page = ShapeSelectionPage()
        self.parameters_page = ParametersPage()

        self.addPage(self.shape_page)
        self.addPage(self.parameters_page)

    def get_build_step(self):
        """Create BuildStep from wizard data"""
        shape_type = self.shape_page.get_selected_shape()
        params = self.parameters_page.get_parameters()

        # Separate repetitions from dimensions
        repetitions = params.pop("repetitions", 1)

        return BuildStep(
            shape_type=shape_type,
            dimensions=params,
            repetitions=repetitions
        )


class EditBuildStepDialog(QDialog):
    """Dialog for editing existing build steps"""

    def __init__(self, parent=None, build_step: Optional[BuildStep] = None):
        super().__init__(parent)
        self.setWindowTitle("Edit Build Step")
        self.setModal(True)
        self.resize(400, 300)

        # Store the original build step
        self.original_build_step = build_step or BuildStep()
        self.current_build_step = BuildStep(
            shape_type=self.original_build_step.shape_type,
            dimensions=self.original_build_step.dimensions.copy(),
            repetitions=self.original_build_step.repetitions
        )

        self.setup_ui()
        self.load_current_values()

    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout()

        # Shape type selection
        shape_layout = QHBoxLayout()
        shape_layout.addWidget(QLabel("Shape Type:"))
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(["Square", "Rectangle", "Circle", "Ellipse"])
        self.shape_combo.currentTextChanged.connect(self.on_shape_changed)
        shape_layout.addWidget(self.shape_combo)
        shape_layout.addStretch()
        layout.addLayout(shape_layout)

        # Dynamic parameters area
        self.parameters_layout = QVBoxLayout()
        layout.addLayout(self.parameters_layout)

        # Repetitions (always present)
        rep_layout = QHBoxLayout()
        rep_layout.addWidget(QLabel("Repetitions:"))
        self.repetitions_edit = QLineEdit()
        rep_layout.addWidget(self.repetitions_edit)
        rep_layout.addStretch()
        layout.addLayout(rep_layout)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        self.save_button.clicked.connect(self.on_save)
        self.cancel_button.clicked.connect(self.on_cancel)

        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Dictionary to store parameter widgets
        self.parameter_widgets = {}

    def load_current_values(self):
        """Load current build step values into the UI"""
        # Set shape type
        shape_index = ["square", "rectangle", "circle", "ellipse"].index(self.current_build_step.shape_type)
        self.shape_combo.setCurrentIndex(shape_index)

        # Set repetitions
        self.repetitions_edit.setText(str(self.current_build_step.repetitions))

        # Setup parameters for current shape
        self.setup_parameters_for_shape(self.current_build_step.shape_type, load_values=True)

    def on_shape_changed(self, shape_text):
        """Handle shape type change"""
        shape_type = shape_text.lower()

        # Clear current dimensions when shape changes (user requested blank fields for new shape)
        self.current_build_step.shape_type = shape_type
        self.current_build_step.dimensions = {}

        # Setup new parameter fields with blank values
        self.setup_parameters_for_shape(shape_type, load_values=False)

    def setup_parameters_for_shape(self, shape_type: str, load_values: bool = True):
        """Setup parameter input fields for the selected shape"""
        # Clear existing parameter widgets
        for i in reversed(range(self.parameters_layout.count())):
            child = self.parameters_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        self.parameter_widgets.clear()

        # Add parameter fields based on shape type
        if shape_type == "square":
            self.add_parameter_field("Size", "size", "mm", load_values)
        elif shape_type == "rectangle":
            self.add_parameter_field("Width", "width", "mm", load_values)
            self.add_parameter_field("Length", "length", "mm", load_values)
        elif shape_type == "circle":
            self.add_parameter_field("Diameter", "diameter", "mm", load_values)
        elif shape_type == "ellipse":
            self.add_parameter_field("Width", "width", "mm", load_values)
            self.add_parameter_field("Length", "length", "mm", load_values)

    def add_parameter_field(self, label_text: str, field_name: str, unit: str, load_value: bool = True):
        """Add a parameter input field"""
        h_layout = QHBoxLayout()

        label = QLabel(f"{label_text}:")
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("0.0")
        unit_label = QLabel(f"[{unit}]")

        # Load existing value if requested and available
        if load_value and field_name in self.current_build_step.dimensions:
            line_edit.setText(str(self.current_build_step.dimensions[field_name]))

        h_layout.addWidget(label)
        h_layout.addWidget(line_edit)
        h_layout.addWidget(unit_label)

        self.parameters_layout.addLayout(h_layout)
        self.parameter_widgets[field_name] = line_edit

    def validate_input(self) -> bool:
        """Validate all input fields"""
        try:
            # Validate repetitions
            repetitions = int(self.repetitions_edit.text())
            if repetitions < 1:
                QMessageBox.warning(self, "Invalid Input", "Repetitions must be at least 1.")
                return False

            # Validate all dimension parameters
            for field_name, widget in self.parameter_widgets.items():
                text = widget.text().strip()
                if not text:
                    QMessageBox.warning(self, "Invalid Input", f"Please enter a value for {field_name}.")
                    return False

                value = float(text)
                if value <= 0:
                    QMessageBox.warning(self, "Invalid Input", f"{field_name} must be greater than 0.")
                    return False

            return True
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numeric values.")
            return False

    def on_save(self):
        """Handle Save button click"""
        if not self.validate_input():
            return

        try:
            # Update the current build step with new values
            self.current_build_step.repetitions = int(self.repetitions_edit.text())

            # Update dimensions
            self.current_build_step.dimensions = {}
            for field_name, widget in self.parameter_widgets.items():
                self.current_build_step.dimensions[field_name] = float(widget.text())

            print(f"Build step updated: {self.current_build_step.to_list_item_text()}")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save build step: {e}")

    def on_cancel(self):
        """Handle Cancel button click"""
        print("Edit build step cancelled")
        self.reject()

    def get_updated_build_step(self) -> BuildStep:
        """Get the updated build step"""
        return self.current_build_step


class Build3DVisualizer(FigureCanvas):
    """3D visualizer for build steps using matplotlib"""

    def __init__(self, parent=None):
        if not MATPLOTLIB_AVAILABLE:
            # Fallback to simple widget
            super(FigureCanvas, self).__init__()
            return

        self.figure = Figure(figsize=(8, 6), dpi=100)
        super().__init__(self.figure)
        self.setParent(parent)

        # Create 3D subplot
        self.ax = self.figure.add_subplot(111, projection='3d')
        self.layer_height = 0.1

        # Set up the plot
        self.ax.set_xlabel('X (mm)')
        self.ax.set_ylabel('Y (mm)')
        self.ax.set_zlabel('Z (mm)')
        self.ax.set_title('Build Visualization')

        print("3D matplotlib visualizer initialized successfully")

    def create_box_vertices(self, width, length, height, offset_x=0, offset_y=0, offset_z=0):
        """Create vertices for a 3D box"""
        w, l, h = width/2, length/2, height/2
        x, y, z = offset_x, offset_y, offset_z

        # Define the vertices of the box
        vertices = [
            [x-w, y-l, z-h], [x+w, y-l, z-h], [x+w, y+l, z-h], [x-w, y+l, z-h],  # bottom
            [x-w, y-l, z+h], [x+w, y-l, z+h], [x+w, y+l, z+h], [x-w, y+l, z+h]   # top
        ]

        # Define the 6 faces of the box
        faces = [
            [vertices[0], vertices[1], vertices[2], vertices[3]],  # bottom
            [vertices[4], vertices[7], vertices[6], vertices[5]],  # top
            [vertices[0], vertices[4], vertices[5], vertices[1]],  # front
            [vertices[2], vertices[6], vertices[7], vertices[3]],  # back
            [vertices[0], vertices[3], vertices[7], vertices[4]],  # left
            [vertices[1], vertices[5], vertices[6], vertices[2]]   # right
        ]

        return faces

    def create_cylinder_faces(self, radius, height, segments=16, offset_x=0, offset_y=0, offset_z=0):
        """Create faces for a 3D cylinder"""
        faces = []
        x, y, z = offset_x, offset_y, offset_z
        h = height / 2

        # Create bottom and top circles
        bottom_circle = []
        top_circle = []

        for i in range(segments):
            angle = 2 * math.pi * i / segments
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            bottom_circle.append([px, py, z - h])
            top_circle.append([px, py, z + h])

        # Add bottom and top faces
        faces.append(bottom_circle)
        faces.append(top_circle[::-1])  # Reverse for correct normal

        # Add side faces
        for i in range(segments):
            next_i = (i + 1) % segments
            face = [
                bottom_circle[i],
                bottom_circle[next_i],
                top_circle[next_i],
                top_circle[i]
            ]
            faces.append(face)

        return faces

    def update_visualization(self, build_steps: list, layer_height: float = 0.1):
        """Update the 3D visualization with build steps"""
        if not MATPLOTLIB_AVAILABLE:
            return

        self.layer_height = layer_height
        self.ax.clear()

        # Set up the plot
        self.ax.set_xlabel('X (mm)')
        self.ax.set_ylabel('Y (mm)')
        self.ax.set_zlabel('Z (mm)')
        self.ax.set_title('Build Visualization')

        if not build_steps:
            self.ax.text(0, 0, 0, "No build steps defined.\nUse 'Add Step' button to create shapes.",
                        fontsize=12, ha='center')
            self.draw()
            return

        current_z = 0
        colors = ['gold', 'lightgreen', 'lightblue', 'lightcoral', 'plum', 'orange']

        for step_index, build_step in enumerate(build_steps):
            color = colors[step_index % len(colors)]
            dims = build_step.dimensions

            # Create each repetition
            for rep in range(build_step.repetitions):
                z_offset = current_z + (layer_height / 2)

                if build_step.shape_type == "square":
                    size = dims.get("size", 10)
                    faces = self.create_box_vertices(size, size, layer_height, 0, 0, z_offset)
                    poly3d = Poly3DCollection(faces, alpha=0.8, facecolor=color, edgecolor='black')
                    self.ax.add_collection3d(poly3d)

                elif build_step.shape_type == "rectangle":
                    width = dims.get("width", 10)
                    length = dims.get("length", 15)
                    faces = self.create_box_vertices(width, length, layer_height, 0, 0, z_offset)
                    poly3d = Poly3DCollection(faces, alpha=0.8, facecolor=color, edgecolor='black')
                    self.ax.add_collection3d(poly3d)

                elif build_step.shape_type == "circle":
                    diameter = dims.get("diameter", 10)
                    radius = diameter / 2
                    faces = self.create_cylinder_faces(radius, layer_height, 16, 0, 0, z_offset)
                    poly3d = Poly3DCollection(faces, alpha=0.8, facecolor=color, edgecolor='black')
                    self.ax.add_collection3d(poly3d)

                elif build_step.shape_type == "ellipse":
                    width = dims.get("width", 10)
                    length = dims.get("length", 15)
                    # Use larger radius and scale for ellipse
                    radius = max(width, length) / 2
                    faces = self.create_cylinder_faces(radius, layer_height, 24, 0, 0, z_offset)

                    # Scale faces to create ellipse
                    scale_x = width / (2 * radius)
                    scale_y = length / (2 * radius)

                    scaled_faces = []
                    for face in faces:
                        scaled_face = []
                        for vertex in face:
                            scaled_vertex = [vertex[0] * scale_x, vertex[1] * scale_y, vertex[2]]
                            scaled_face.append(scaled_vertex)
                        scaled_faces.append(scaled_face)

                    poly3d = Poly3DCollection(scaled_faces, alpha=0.8, facecolor=color, edgecolor='black')
                    self.ax.add_collection3d(poly3d)

                current_z += layer_height

        # Set axis limits and aspect ratio
        if build_steps:
            max_dim = 0
            for build_step in build_steps:
                dims = build_step.dimensions
                if build_step.shape_type == "square":
                    max_dim = max(max_dim, dims.get("size", 10))
                elif build_step.shape_type in ["rectangle", "ellipse"]:
                    max_dim = max(max_dim, dims.get("width", 10), dims.get("length", 15))
                elif build_step.shape_type == "circle":
                    max_dim = max(max_dim, dims.get("diameter", 10))

            limit = max_dim / 2 * 1.2
            self.ax.set_xlim([-limit, limit])
            self.ax.set_ylim([-limit, limit])
            self.ax.set_zlim([0, current_z * 1.1])

        # Set viewing angle
        self.ax.view_init(elev=30, azim=45)
        self.draw()


class RecoaterDialog(QDialog):
    """Dialog for configuring recoater blade settings"""

    def __init__(self, parent=None, settings: Optional[RecoaterSettings] = None):
        super().__init__(parent)
        # Load the UI file
        uic.loadUi('v0_recoater_dialog.ui', self)

        # Store reference to current settings
        self.settings = settings or RecoaterSettings()
        self.temp_settings = RecoaterSettings()

        # Set initial values from current settings
        self.load_settings_to_ui()

        # Connect signals
        self.pushButton.clicked.connect(self.on_use_modified_settings)  # Use Modified Settings
        self.pushButton_2.clicked.connect(self.on_cancel)               # Cancel

        # Connect line edit changes to update temp settings
        self.lineEdit.textChanged.connect(self.update_temp_settings)      # Advance velocity
        self.lineEdit_2.textChanged.connect(self.update_temp_settings)    # Retract velocity
        self.lineEdit_3.textChanged.connect(self.update_temp_settings)    # Dwell time
        self.lineEdit_6.textChanged.connect(self.update_temp_settings)    # Full repeats
        self.lineEdit_7.textChanged.connect(self.update_temp_settings)    # Cycle repeats

    def load_settings_to_ui(self):
        """Load current settings values into the UI controls"""
        self.lineEdit.setText(str(self.settings.advance_velocity))
        self.lineEdit_2.setText(str(self.settings.retract_velocity))
        self.lineEdit_3.setText(str(self.settings.dwell_time))
        self.lineEdit_6.setText(str(self.settings.full_repeats))
        self.lineEdit_7.setText(str(self.settings.cycle_repeats))

        # Also update temp settings
        self.temp_settings = RecoaterSettings(
            advance_velocity=self.settings.advance_velocity,
            retract_velocity=self.settings.retract_velocity,
            dwell_time=self.settings.dwell_time,
            full_repeats=self.settings.full_repeats,
            cycle_repeats=self.settings.cycle_repeats
        )

    def update_temp_settings(self):
        """Update temporary settings based on current UI values"""
        try:
            self.temp_settings.advance_velocity = float(self.lineEdit.text() or "0")
            self.temp_settings.retract_velocity = float(self.lineEdit_2.text() or "0")
            self.temp_settings.dwell_time = float(self.lineEdit_3.text() or "0")
            self.temp_settings.full_repeats = int(self.lineEdit_6.text() or "0")
            self.temp_settings.cycle_repeats = int(self.lineEdit_7.text() or "0")
        except ValueError:
            # Ignore invalid values during typing
            pass

    def on_use_modified_settings(self):
        """Handle Use Modified Settings button - update settings and close"""
        try:
            # Validate and update the actual settings
            self.settings.advance_velocity = self.temp_settings.advance_velocity
            self.settings.retract_velocity = self.temp_settings.retract_velocity
            self.settings.dwell_time = self.temp_settings.dwell_time
            self.settings.full_repeats = self.temp_settings.full_repeats
            self.settings.cycle_repeats = self.temp_settings.cycle_repeats

            print(f"Recoater settings updated: {self.settings}")
            self.accept()  # Close dialog with "accepted" status
        except Exception as e:
            print(f"Error updating recoater settings: {e}")

    def on_cancel(self):
        """Handle Cancel button - close dialog without updating settings"""
        print("Recoater dialog cancelled")
        self.reject()  # Close dialog with "rejected" status


class MainWindow(QMainWindow):
    """Main application window with UI signals connected"""

    def __init__(self):
        super().__init__()
        # Load the UI file
        uic.loadUi('v0_yeahobpuknowme.ui', self)

        # Initialize recoater settings
        self.recoater_settings = RecoaterSettings()

        # Initialize the 3D build visualizer
        try:
            if MATPLOTLIB_AVAILABLE:
                self.build_visualizer = Build3DVisualizer(self)

                # Replace the graphics view with matplotlib widget
                graphics_parent = self.gview_visualizer.parent()
                if graphics_parent and hasattr(graphics_parent, 'layout') and graphics_parent.layout():
                    parent_layout = graphics_parent.layout()
                    # Get the index of the graphics view in the layout
                    for i in range(parent_layout.count()):
                        if parent_layout.itemAt(i).widget() == self.gview_visualizer:
                            # Remove the old widget
                            parent_layout.removeWidget(self.gview_visualizer)
                            self.gview_visualizer.setParent(None)
                            # Insert the new visualizer at the same position
                            parent_layout.insertWidget(i, self.build_visualizer)
                            break

                    # Update reference
                    self.gview_visualizer = self.build_visualizer
                    print("3D matplotlib visualizer integrated successfully")
                else:
                    print("Could not find parent layout for graphics view")
                    self.build_visualizer = None
            else:
                print("Matplotlib not available - 3D visualization disabled")
                self.build_visualizer = None

        except Exception as e:
            print(f"Failed to initialize 3D visualizer: {e}")
            self.build_visualizer = None

        # Connect line edit signals (editingFinished)
        self.le_spotsize.editingFinished.connect(self.on_beam_spot_size_changed)
        self.le_beampower.editingFinished.connect(self.on_beam_power_changed)
        self.le_layerheight.editingFinished.connect(self.on_layer_height_changed)

        # Connect button signals (clicked)
        self.btn_add_buildstep.clicked.connect(self.on_add_step_clicked)
        self.btn_edit_buildstep.clicked.connect(self.on_edit_step_clicked)
        self.btn_del_buildstep.clicked.connect(self.on_delete_step_clicked)

        # Add move up/down buttons programmatically
        self.add_move_buttons()
        self.btn_recoater_settings.clicked.connect(self.on_view_recoater_settings_clicked)
        self.btn_genpackage.clicked.connect(self.on_generate_build_package_clicked)

        # Connect checkbox signals (toggled)
        self.enable_heatbalance.toggled.connect(self.on_heat_balance_toggled)
        self.enable_jumpsafe.toggled.connect(self.on_jump_safe_toggled)
        self.enable_splattersafe.toggled.connect(self.on_splatter_safe_toggled)
        self.enable_triggeredstart.toggled.connect(self.on_triggered_start_toggled)

        # Connect list widget signals
        self.build_step_list.itemClicked.connect(self.on_build_sequence_item_clicked)
        self.build_step_list.currentItemChanged.connect(self.on_build_sequence_selection_changed)

        # Connect layer height changes to visualizer update
        self.le_layerheight.textChanged.connect(self.update_visualizer)

        # Set default values
        self.set_default_values()

        # Fix main layout proportions
        self.fix_layout_proportions()

    def set_default_values(self):
        """Set sane default values for the UI"""
        # Set beam parameters
        self.le_spotsize.setText("100")  # Spot size 100 microns
        self.le_beampower.setText("100")  # Power 100 watts
        self.le_layerheight.setText("0.1")  # Layer height 0.1 mm

        # Clear existing build steps from the UI file
        self.build_step_list.clear()

        print("Default values set: Spot Size=100μm, Power=100W, Layer Height=0.1mm")

    def fix_layout_proportions(self):
        """Fix the main layout to give proper proportions"""
        try:
            # Get the main horizontal layout (horizontalLayout)
            main_h_layout = self.centralWidget().layout().itemAt(0).layout()

            if main_h_layout:
                # Set stretch factors: left column = 1, right column = 4 (80% width)
                main_h_layout.setStretchFactor(0, 1)  # Left column (controls)
                main_h_layout.setStretchFactor(1, 4)  # Right column (visualizer)
                print("Layout proportions fixed: 20% controls, 80% visualizer")
            else:
                print("Could not find main horizontal layout")
        except Exception as e:
            print(f"Failed to fix layout proportions: {e}")

    def add_move_buttons(self):
        """Add move up/down buttons below the existing build step buttons"""
        try:
            # Find the vertical layout that contains the build step controls
            # We need to go up the parent hierarchy to find the right spot
            build_step_list_parent = self.build_step_list.parent()
            if build_step_list_parent and hasattr(build_step_list_parent, 'layout'):
                parent_layout = build_step_list_parent.layout()

                # Create a new horizontal layout for move buttons
                move_button_layout = QHBoxLayout()

                # Create move up and down buttons
                self.btn_move_up = QPushButton("Move Up")
                self.btn_move_down = QPushButton("Move Down")

                # Add buttons to the new layout
                move_button_layout.addWidget(self.btn_move_up)
                move_button_layout.addWidget(self.btn_move_down)

                # Find where to insert the new layout (after the existing button layout)
                # Look for the existing button layout and insert after it
                for i in range(parent_layout.count()):
                    item = parent_layout.itemAt(i)
                    if item and item.layout():
                        # Check if this layout contains our existing buttons
                        layout = item.layout()
                        for j in range(layout.count()):
                            widget_item = layout.itemAt(j)
                            if widget_item and widget_item.widget() == self.btn_add_buildstep:
                                # Insert the move button layout right after this one
                                parent_layout.insertLayout(i + 1, move_button_layout)
                                print("Move up/down buttons added successfully below existing buttons")

                                # Connect signals
                                self.btn_move_up.clicked.connect(self.on_move_up_clicked)
                                self.btn_move_down.clicked.connect(self.on_move_down_clicked)
                                return

                # If we couldn't find the right spot, add at the end
                parent_layout.addLayout(move_button_layout)

                # Connect signals
                self.btn_move_up.clicked.connect(self.on_move_up_clicked)
                self.btn_move_down.clicked.connect(self.on_move_down_clicked)

                print("Move up/down buttons added at end of layout")
            else:
                print("Could not find parent layout for build step controls")
        except Exception as e:
            print(f"Failed to add move buttons: {e}")

    def get_current_build_steps(self):
        """Get all build steps from the list widget"""
        build_steps = []
        for i in range(self.build_step_list.count()):
            item = self.build_step_list.item(i)
            if item:
                build_step = BuildStep.from_list_item_text(item.text())
                build_steps.append(build_step)
        return build_steps

    def get_layer_height(self):
        """Get current layer height value"""
        try:
            text = self.le_layerheight.text().strip()
            if text:
                return float(text)
            return 0.1  # Default layer height
        except ValueError:
            return 0.1

    def update_visualizer(self):
        """Update the build visualizer with current build steps and layer height"""
        if hasattr(self, 'build_visualizer') and self.build_visualizer:
            build_steps = self.get_current_build_steps()
            layer_height = self.get_layer_height()
            self.build_visualizer.update_visualization(build_steps, layer_height)

    # Line Edit dummy handlers
    def on_beam_spot_size_changed(self):
        """Handle beam spot size editing finished"""
        value = self.le_spotsize.text()
        print(f"Beam Spot Size changed: {value}")

    def on_beam_power_changed(self):
        """Handle beam power editing finished"""
        value = self.le_beampower.text()
        print(f"Beam Power changed: {value}")

    def on_layer_height_changed(self):
        """Handle layer height editing finished"""
        value = self.le_layerheight.text()
        print(f"Layer Height changed: {value}")

    # Button dummy handlers
    def on_add_step_clicked(self):
        """Handle Add Step button clicked"""
        print("Opening Add Build Step wizard")
        wizard = BuildStepWizard(self)
        result = wizard.exec()

        if result == QWizard.DialogCode.Accepted:
            # Get the completed build step
            build_step = wizard.get_build_step()

            # Create list item with formatted text
            item_text = build_step.to_list_item_text()
            item = QListWidgetItem(item_text)

            # Add to the build step list
            self.build_step_list.addItem(item)

            # Update 3D visualizer
            self.update_visualizer()

            print(f"Added build step: {item_text}")
        else:
            print("Build step wizard cancelled")

    def on_edit_step_clicked(self):
        """Handle Edit Step button clicked"""
        # Get the currently selected item
        current_item = self.build_step_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "No Selection", "Please select a build step to edit.")
            return

        # Parse the build step from the list item text
        build_step = BuildStep.from_list_item_text(current_item.text())

        print(f"Editing build step: {current_item.text()}")

        # Create and show the edit dialog
        dialog = EditBuildStepDialog(self, build_step)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            # Get the updated build step
            updated_build_step = dialog.get_updated_build_step()

            # Update the list item text
            current_item.setText(updated_build_step.to_list_item_text())

            # Update 3D visualizer
            self.update_visualizer()

            print(f"Build step updated to: {updated_build_step.to_list_item_text()}")
        else:
            print("Edit build step cancelled")

    def on_delete_step_clicked(self):
        """Handle Delete Step button clicked"""
        # Get the currently selected item
        current_item = self.build_step_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "No Selection", "Please select a build step to delete.")
            return

        # Confirm deletion
        item_text = current_item.text()
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete this build step?\n\n{item_text}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Get the row index and remove the item
            row = self.build_step_list.row(current_item)
            removed_item = self.build_step_list.takeItem(row)

            # Update 3D visualizer
            self.update_visualizer()

            print(f"Deleted build step: {item_text}")

            # Clean up the item
            del removed_item
        else:
            print("Delete build step cancelled")

    def on_move_up_clicked(self):
        """Handle Move Up button clicked"""
        current_row = self.build_step_list.currentRow()
        if current_row <= 0:
            QMessageBox.information(self, "Cannot Move", "Cannot move the first item up or no item selected.")
            return

        # Get the current item
        current_item = self.build_step_list.takeItem(current_row)
        if current_item:
            # Insert it one position up
            self.build_step_list.insertItem(current_row - 1, current_item)
            self.build_step_list.setCurrentRow(current_row - 1)

            # Update visualizer
            self.update_visualizer()

            print(f"Moved build step up: {current_item.text()}")

    def on_move_down_clicked(self):
        """Handle Move Down button clicked"""
        current_row = self.build_step_list.currentRow()
        total_items = self.build_step_list.count()

        if current_row < 0 or current_row >= total_items - 1:
            QMessageBox.information(self, "Cannot Move", "Cannot move the last item down or no item selected.")
            return

        # Get the current item
        current_item = self.build_step_list.takeItem(current_row)
        if current_item:
            # Insert it one position down
            self.build_step_list.insertItem(current_row + 1, current_item)
            self.build_step_list.setCurrentRow(current_row + 1)

            # Update visualizer
            self.update_visualizer()

            print(f"Moved build step down: {current_item.text()}")

    def on_view_recoater_settings_clicked(self):
        """Handle View Recoater Blade Settings button clicked"""
        print("Opening Recoater Blade Settings dialog")
        dialog = RecoaterDialog(self, self.recoater_settings)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            print("Recoater settings accepted and applied")
        else:
            print("Recoater settings dialog cancelled")

    def on_generate_build_package_clicked(self):
        """Handle Generate Build Package button clicked"""
        print("Generate Build Package button clicked")

    # Checkbox dummy handlers
    def on_heat_balance_toggled(self, checked):
        """Handle heatBalance checkbox toggled"""
        print(f"Heat Balance toggled: {checked}")

    def on_jump_safe_toggled(self, checked):
        """Handle jumpSafe checkbox toggled"""
        print(f"Jump Safe toggled: {checked}")

    def on_splatter_safe_toggled(self, checked):
        """Handle splatterSafe checkbox toggled"""
        print(f"Splatter Safe toggled: {checked}")

    def on_triggered_start_toggled(self, checked):
        """Handle triggeredStart checkbox toggled"""
        print(f"Triggered Start toggled: {checked}")

    # List widget dummy handlers
    def on_build_sequence_item_clicked(self, item):
        """Handle build sequence item clicked"""
        print(f"Build Sequence item clicked: {item.text()}")

    def on_build_sequence_selection_changed(self, current, previous):
        """Handle build sequence selection changed"""
        if current:
            print(f"Build Sequence selection changed to: {current.text()}")


def main():
    """Application entry point"""
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
