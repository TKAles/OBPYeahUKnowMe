"""
Wizard classes for creating and configuring build steps
"""

from PyQt6.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
                              QRadioButton, QLabel, QLineEdit, QButtonGroup)
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
