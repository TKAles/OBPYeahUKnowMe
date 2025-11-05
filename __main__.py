"""
Main application entry point for OBP Yeah U Know Me
"""

import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    """Main application window with UI signals connected"""

    def __init__(self):
        super().__init__()
        # Load the UI file
        uic.loadUi('v0_yeahobpuknowme.ui', self)

        # Connect line edit signals (editingFinished)
        self.lineEdit.editingFinished.connect(self.on_beam_spot_size_changed)
        self.lineEdit_2.editingFinished.connect(self.on_beam_power_changed)
        self.lineEdit_3.editingFinished.connect(self.on_layer_height_changed)

        # Connect button signals (clicked)
        self.pushButton.clicked.connect(self.on_add_step_clicked)
        self.pushButton_5.clicked.connect(self.on_edit_step_clicked)
        self.pushButton_2.clicked.connect(self.on_delete_step_clicked)
        self.pushButton_4.clicked.connect(self.on_view_recoater_settings_clicked)
        self.pushButton_3.clicked.connect(self.on_generate_build_package_clicked)

        # Connect checkbox signals (toggled)
        self.checkBox_3.toggled.connect(self.on_heat_balance_toggled)
        self.checkBox_2.toggled.connect(self.on_jump_safe_toggled)
        self.checkBox.toggled.connect(self.on_splatter_safe_toggled)
        self.checkBox_4.toggled.connect(self.on_triggered_start_toggled)

        # Connect list widget signals
        self.listWidget.itemClicked.connect(self.on_build_sequence_item_clicked)
        self.listWidget.currentItemChanged.connect(self.on_build_sequence_selection_changed)

    # Line Edit dummy handlers
    def on_beam_spot_size_changed(self):
        """Handle beam spot size editing finished"""
        value = self.lineEdit.text()
        print(f"Beam Spot Size changed: {value}")

    def on_beam_power_changed(self):
        """Handle beam power editing finished"""
        value = self.lineEdit_2.text()
        print(f"Beam Power changed: {value}")

    def on_layer_height_changed(self):
        """Handle layer height editing finished"""
        value = self.lineEdit_3.text()
        print(f"Layer Height changed: {value}")

    # Button dummy handlers
    def on_add_step_clicked(self):
        """Handle Add Step button clicked"""
        print("Add Step button clicked")

    def on_edit_step_clicked(self):
        """Handle Edit Step button clicked"""
        print("Edit Step button clicked")

    def on_delete_step_clicked(self):
        """Handle Delete Step button clicked"""
        print("Delete Step button clicked")

    def on_view_recoater_settings_clicked(self):
        """Handle View Recoater Blade Settings button clicked"""
        print("View Recoater Blade Settings button clicked")

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
