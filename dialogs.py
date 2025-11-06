"""
Dialog classes for editing build steps and recoater settings
"""

from typing import Optional
from PyQt6 import uic
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QComboBox, QMessageBox, QCheckBox)
from models import BuildStep, RecoaterSettings


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
            repetitions=self.original_build_step.repetitions,
            x_offset=self.original_build_step.x_offset,
            y_offset=self.original_build_step.y_offset,
            starting_layer=self.original_build_step.starting_layer
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

        # X Offset field
        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel("X Offset:"))
        self.x_offset_edit = QLineEdit()
        x_layout.addWidget(self.x_offset_edit)
        x_layout.addWidget(QLabel("[mm]"))
        x_layout.addStretch()
        layout.addLayout(x_layout)

        # Y Offset field
        y_layout = QHBoxLayout()
        y_layout.addWidget(QLabel("Y Offset:"))
        self.y_offset_edit = QLineEdit()
        y_layout.addWidget(self.y_offset_edit)
        y_layout.addWidget(QLabel("[mm]"))
        y_layout.addStretch()
        layout.addLayout(y_layout)

        # Starting layer checkbox
        self.enable_starting_layer = QCheckBox("Enable custom starting layer")
        self.enable_starting_layer.toggled.connect(self.on_starting_layer_toggled)
        layout.addWidget(self.enable_starting_layer)

        # Starting layer field
        layer_layout = QHBoxLayout()
        layer_layout.addWidget(QLabel("Starting Layer:"))
        self.starting_layer_edit = QLineEdit()
        self.starting_layer_edit.setEnabled(False)
        layer_layout.addWidget(self.starting_layer_edit)
        layer_layout.addStretch()
        layout.addLayout(layer_layout)

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

        # Set offsets
        self.x_offset_edit.setText(str(self.current_build_step.x_offset))
        self.y_offset_edit.setText(str(self.current_build_step.y_offset))

        # Set starting layer
        self.starting_layer_edit.setText(str(self.current_build_step.starting_layer))
        if self.current_build_step.starting_layer > 0:
            self.enable_starting_layer.setChecked(True)
            self.starting_layer_edit.setEnabled(True)
        else:
            self.enable_starting_layer.setChecked(False)
            self.starting_layer_edit.setEnabled(False)

        # Setup parameters for current shape
        self.setup_parameters_for_shape(self.current_build_step.shape_type, load_values=True)

    def on_starting_layer_toggled(self, checked):
        """Enable/disable starting layer input based on checkbox"""
        self.starting_layer_edit.setEnabled(checked)
        if not checked:
            self.starting_layer_edit.setText("0")

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

            # Validate offsets (can be any float value)
            float(self.x_offset_edit.text())
            float(self.y_offset_edit.text())

            # Validate starting layer
            starting_layer = int(self.starting_layer_edit.text())
            if starting_layer < 0:
                QMessageBox.warning(self, "Invalid Input", "Starting layer cannot be negative.")
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

            # Update offsets
            self.current_build_step.x_offset = float(self.x_offset_edit.text())
            self.current_build_step.y_offset = float(self.y_offset_edit.text())

            # Update starting layer
            if self.enable_starting_layer.isChecked():
                self.current_build_step.starting_layer = int(self.starting_layer_edit.text())
            else:
                self.current_build_step.starting_layer = 0

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
