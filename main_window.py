"""
Main window class for OBP Yeah U Know Me application
"""

from PyQt6 import uic
from PyQt6.QtWidgets import (QMainWindow, QSizePolicy, QVBoxLayout, QWizard,
                              QDialog, QListWidgetItem, QMessageBox)
from models import RecoaterSettings, BuildStep
from wizard import BuildStepWizard
from dialogs import EditBuildStepDialog, RecoaterDialog
from visualization import Build3DVisualizer


class MainWindow(QMainWindow):
    """Main application window with UI signals connected"""

    def __init__(self, parent=None):
        super().__init__()
        # Load the UI file
        uic.loadUi('v0_yeahobpuknowme.ui', self)

        # Initialize recoater settings
        self.recoater_settings = RecoaterSettings()

        # Initialize the 3D build visualizer
        self.build_visualizer = Build3DVisualizer()

        self.vis_layout = self.findChild(QVBoxLayout, "visualization_layout")
        self.vis_layout.addWidget(self.build_visualizer)
        # Connect line edit signals (editingFinished)
        self.le_spotsize.editingFinished.connect(self.on_beam_spot_size_changed)
        self.le_beampower.editingFinished.connect(self.on_beam_power_changed)
        self.le_layerheight.editingFinished.connect(self.on_layer_height_changed)

        # Connect button signals (clicked)
        self.btn_add_buildstep.clicked.connect(self.on_add_step_clicked)
        self.btn_edit_buildstep.clicked.connect(self.on_edit_step_clicked)
        self.btn_del_buildstep.clicked.connect(self.on_delete_step_clicked)

        # Connect move up/down button signals
        self.btn_move_up.clicked.connect(self.on_move_up_clicked)
        self.btn_move_down.clicked.connect(self.on_move_down_clicked)
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
        self.build_visualizer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Set default values
        self.set_default_values()

    def set_default_values(self):
        """Set sane default values for the UI"""
        # Set beam parameters
        self.le_spotsize.setText("100")  # Spot size 100 microns
        self.le_beampower.setText("100")  # Power 100 watts
        self.le_layerheight.setText("0.1")  # Layer height 0.1 mm

        # Clear existing build steps from the UI file
        self.build_step_list.clear()

        print("Default values set: Spot Size=100μm, Power=100W, Layer Height=0.1mm")

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
