"""
Wizard classes for creating and configuring build steps
"""

from PyQt6.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
                              QRadioButton, QLabel, QLineEdit, QButtonGroup, QCheckBox, QComboBox)
from models import BuildStep


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


class PositionPage(QWizardPage):
    """Third page of wizard - input position and layer settings"""

    def __init__(self):
        super().__init__()
        self.setTitle("Position & Layer Settings")
        self.setSubTitle("Configure the position offset and starting layer:")

        layout = QVBoxLayout()

        # X Offset field
        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel("X Offset:"))
        self.x_offset_edit = QLineEdit()
        self.x_offset_edit.setPlaceholderText("0.0")
        self.x_offset_edit.setText("0.0")
        x_layout.addWidget(self.x_offset_edit)
        x_layout.addWidget(QLabel("[mm]"))
        layout.addLayout(x_layout)

        # Y Offset field
        y_layout = QHBoxLayout()
        y_layout.addWidget(QLabel("Y Offset:"))
        self.y_offset_edit = QLineEdit()
        self.y_offset_edit.setPlaceholderText("0.0")
        self.y_offset_edit.setText("0.0")
        y_layout.addWidget(self.y_offset_edit)
        y_layout.addWidget(QLabel("[mm]"))
        layout.addLayout(y_layout)

        # Add spacing
        layout.addSpacing(20)

        # Starting layer checkbox
        self.enable_starting_layer = QCheckBox("Enable custom starting layer")
        self.enable_starting_layer.setChecked(False)
        self.enable_starting_layer.toggled.connect(self.on_starting_layer_toggled)
        layout.addWidget(self.enable_starting_layer)

        # Starting layer field
        layer_layout = QHBoxLayout()
        layer_layout.addWidget(QLabel("Starting Layer:"))
        self.starting_layer_edit = QLineEdit()
        self.starting_layer_edit.setPlaceholderText("0")
        self.starting_layer_edit.setText("0")
        self.starting_layer_edit.setEnabled(False)
        layer_layout.addWidget(self.starting_layer_edit)
        layer_layout.addWidget(QLabel("(0 = build from bottom)"))
        layout.addLayout(layer_layout)

        # Add info label
        info_label = QLabel(
            "Note: Custom starting layer allows building multiple objects\n"
            "at different Z-heights (e.g., for building separate parts)."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(info_label)

        layout.addStretch()
        self.setLayout(layout)

        # Connect validation signals
        self.x_offset_edit.textChanged.connect(self.completeChanged.emit)
        self.y_offset_edit.textChanged.connect(self.completeChanged.emit)
        self.starting_layer_edit.textChanged.connect(self.completeChanged.emit)

    def on_starting_layer_toggled(self, checked):
        """Enable/disable starting layer input based on checkbox"""
        self.starting_layer_edit.setEnabled(checked)
        if not checked:
            self.starting_layer_edit.setText("0")

    def isComplete(self):
        """Page is complete when all fields have valid values"""
        try:
            # Validate offsets
            float(self.x_offset_edit.text())
            float(self.y_offset_edit.text())

            # Validate starting layer
            layer = int(self.starting_layer_edit.text())
            if layer < 0:
                return False

            return True
        except (ValueError, TypeError):
            return False

    def get_position_data(self):
        """Get the position and layer data"""
        try:
            return {
                "x_offset": float(self.x_offset_edit.text()),
                "y_offset": float(self.y_offset_edit.text()),
                "starting_layer": int(self.starting_layer_edit.text()) if self.enable_starting_layer.isChecked() else 0
            }
        except (ValueError, TypeError):
            return {"x_offset": 0.0, "y_offset": 0.0, "starting_layer": 0}


class HatchingPage(QWizardPage):
    """Fourth page of wizard - configure hatching parameters"""

    def __init__(self):
        super().__init__()
        self.setTitle("Hatching Configuration")
        self.setSubTitle("Configure scan pattern parameters for laser hatching:")

        layout = QVBoxLayout()

        # Enable hatching checkbox
        self.enable_hatching = QCheckBox("Enable hatching")
        self.enable_hatching.setChecked(False)
        self.enable_hatching.toggled.connect(self.on_hatching_toggled)
        layout.addWidget(self.enable_hatching)

        layout.addSpacing(10)

        # Hatch spacing field
        spacing_layout = QHBoxLayout()
        spacing_layout.addWidget(QLabel("Hatch Spacing:"))
        self.hatch_spacing_edit = QLineEdit()
        self.hatch_spacing_edit.setPlaceholderText("0.1")
        self.hatch_spacing_edit.setText("0.1")
        self.hatch_spacing_edit.setEnabled(False)
        spacing_layout.addWidget(self.hatch_spacing_edit)
        spacing_layout.addWidget(QLabel("[mm]"))
        layout.addLayout(spacing_layout)

        # Hatch angle field
        angle_layout = QHBoxLayout()
        angle_layout.addWidget(QLabel("Hatch Angle:"))
        self.hatch_angle_edit = QLineEdit()
        self.hatch_angle_edit.setPlaceholderText("0.0")
        self.hatch_angle_edit.setText("0.0")
        self.hatch_angle_edit.setEnabled(False)
        angle_layout.addWidget(self.hatch_angle_edit)
        angle_layout.addWidget(QLabel("[degrees]"))
        layout.addLayout(angle_layout)

        # Hatch pattern selection
        pattern_layout = QHBoxLayout()
        pattern_layout.addWidget(QLabel("Hatch Pattern:"))
        self.hatch_pattern_combo = QComboBox()
        self.hatch_pattern_combo.addItems(["linear", "crosshatch"])
        self.hatch_pattern_combo.setEnabled(False)
        pattern_layout.addWidget(self.hatch_pattern_combo)
        pattern_layout.addStretch()
        layout.addLayout(pattern_layout)

        # Add info label
        info_label = QLabel(
            "Note: Hatching generates laser scan paths as start/end point pairs.\n"
            "• Spacing: Distance between parallel scan lines\n"
            "• Angle: Rotation of scan pattern (0° = horizontal)\n"
            "• Linear: Single direction scan\n"
            "• Crosshatch: Perpendicular scan pattern (0° + 90°)"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addSpacing(10)
        layout.addWidget(info_label)

        layout.addStretch()
        self.setLayout(layout)

        # Connect validation signals
        self.hatch_spacing_edit.textChanged.connect(self.completeChanged.emit)
        self.hatch_angle_edit.textChanged.connect(self.completeChanged.emit)

    def on_hatching_toggled(self, checked):
        """Enable/disable hatching inputs based on checkbox"""
        self.hatch_spacing_edit.setEnabled(checked)
        self.hatch_angle_edit.setEnabled(checked)
        self.hatch_pattern_combo.setEnabled(checked)

    def isComplete(self):
        """Page is complete when all fields have valid values or hatching is disabled"""
        if not self.enable_hatching.isChecked():
            return True

        try:
            # Validate spacing
            spacing = float(self.hatch_spacing_edit.text())
            if spacing <= 0:
                return False

            # Validate angle
            float(self.hatch_angle_edit.text())

            return True
        except (ValueError, TypeError):
            return False

    def get_hatching_data(self):
        """Get the hatching configuration data"""
        try:
            return {
                "hatching_enabled": self.enable_hatching.isChecked(),
                "hatch_spacing": float(self.hatch_spacing_edit.text()) if self.enable_hatching.isChecked() else 0.1,
                "hatch_angle": float(self.hatch_angle_edit.text()) if self.enable_hatching.isChecked() else 0.0,
                "hatch_pattern": self.hatch_pattern_combo.currentText() if self.enable_hatching.isChecked() else "linear"
            }
        except (ValueError, TypeError):
            return {
                "hatching_enabled": False,
                "hatch_spacing": 0.1,
                "hatch_angle": 0.0,
                "hatch_pattern": "linear"
            }


class BuildStepWizard(QWizard):
    """Wizard for creating new build steps"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Build Step")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)

        # Add pages
        self.shape_page = ShapeSelectionPage()
        self.parameters_page = ParametersPage()
        self.position_page = PositionPage()
        self.hatching_page = HatchingPage()

        self.addPage(self.shape_page)
        self.addPage(self.parameters_page)
        self.addPage(self.position_page)
        self.addPage(self.hatching_page)

    def get_build_step(self):
        """Create BuildStep from wizard data"""
        shape_type = self.shape_page.get_selected_shape()
        params = self.parameters_page.get_parameters()
        position_data = self.position_page.get_position_data()
        hatching_data = self.hatching_page.get_hatching_data()

        # Separate repetitions from dimensions
        repetitions = params.pop("repetitions", 1)

        return BuildStep(
            shape_type=shape_type,
            dimensions=params,
            repetitions=repetitions,
            x_offset=position_data["x_offset"],
            y_offset=position_data["y_offset"],
            starting_layer=position_data["starting_layer"],
            hatching_enabled=hatching_data["hatching_enabled"],
            hatch_spacing=hatching_data["hatch_spacing"],
            hatch_angle=hatching_data["hatch_angle"],
            hatch_pattern=hatching_data["hatch_pattern"]
        )
