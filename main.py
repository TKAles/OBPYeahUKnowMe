#!/usr/bin/env python3
"""
OBP Yeah You Know Me - Main Application
3D Additive Manufacturing Build Package Generator
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6 import uic
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class MatplotlibCanvas(FigureCanvas):
    """Matplotlib canvas widget for embedding in Qt application"""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111, projection='3d')
        super().__init__(self.fig)
        self.setParent(parent)

        # Set up default 3D view
        self.setup_default_view()

    def setup_default_view(self):
        """Setup a default 3D view showing a build platform and coordinate system"""
        # Clear the axes
        self.axes.clear()

        # Create a build platform (base plate)
        x_platform = np.linspace(-50, 50, 10)
        y_platform = np.linspace(-50, 50, 10)
        X_platform, Y_platform = np.meshgrid(x_platform, y_platform)
        Z_platform = np.zeros_like(X_platform)

        # Plot the build platform
        self.axes.plot_surface(X_platform, Y_platform, Z_platform,
                              alpha=0.3, color='lightgray',
                              edgecolors='gray', linewidth=0.5)

        # Add coordinate axes
        axis_length = 60
        self.axes.quiver(0, 0, 0, axis_length, 0, 0,
                        color='red', arrow_length_ratio=0.1, linewidth=2, label='X')
        self.axes.quiver(0, 0, 0, 0, axis_length, 0,
                        color='green', arrow_length_ratio=0.1, linewidth=2, label='Y')
        self.axes.quiver(0, 0, 0, 0, 0, axis_length,
                        color='blue', arrow_length_ratio=0.1, linewidth=2, label='Z')

        # Add example build volume boundary
        build_size = 50
        # Draw build volume edges
        corners = [
            [[-build_size, build_size], [-build_size, -build_size], [0, 0]],
            [[-build_size, build_size], [build_size, build_size], [0, 0]],
            [[build_size, build_size], [-build_size, build_size], [0, 0]],
            [[-build_size, -build_size], [-build_size, build_size], [0, 0]],

            [[-build_size, build_size], [-build_size, -build_size], [build_size*2, build_size*2]],
            [[-build_size, build_size], [build_size, build_size], [build_size*2, build_size*2]],
            [[build_size, build_size], [-build_size, build_size], [build_size*2, build_size*2]],
            [[-build_size, -build_size], [-build_size, build_size], [build_size*2, build_size*2]],

            [[-build_size, -build_size], [-build_size, -build_size], [0, build_size*2]],
            [[build_size, build_size], [build_size, build_size], [0, build_size*2]],
            [[-build_size, -build_size], [build_size, build_size], [0, build_size*2]],
            [[build_size, build_size], [-build_size, -build_size], [0, build_size*2]],
        ]

        for corner in corners:
            self.axes.plot(corner[0], corner[1], corner[2], 'k--', alpha=0.3, linewidth=0.5)

        # Set labels
        self.axes.set_xlabel('X [mm]', fontsize=10)
        self.axes.set_ylabel('Y [mm]', fontsize=10)
        self.axes.set_zlabel('Z [mm]', fontsize=10)

        # Set limits
        self.axes.set_xlim([-60, 60])
        self.axes.set_ylim([-60, 60])
        self.axes.set_zlim([0, 120])

        # Set title
        self.axes.set_title('Build Volume Visualizer\n(Awaiting build sequence)',
                           fontsize=12, pad=10)

        # Set viewing angle
        self.axes.view_init(elev=20, azim=45)

        # Add grid
        self.axes.grid(True, alpha=0.3)

        # Tight layout
        self.fig.tight_layout()

        # Refresh canvas
        self.draw()


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()

        # Load the UI file
        uic.loadUi('v0_yeahobpuknowme.ui', self)

        # Replace the QGraphicsView with matplotlib canvas
        self.setup_matplotlib_canvas()

        # Connect signals
        self.setup_connections()

    def setup_matplotlib_canvas(self):
        """Replace the QGraphicsView with a matplotlib canvas"""
        # Find the graphics view widget
        graphics_view = self.findChild(QWidget, 'graphicsView')

        if graphics_view:
            # Get the parent layout
            parent_layout = graphics_view.parent().layout()

            # Find the index of the graphics view in the layout
            for i in range(parent_layout.count()):
                if parent_layout.itemAt(i).widget() == graphics_view:
                    # Remove the old widget
                    parent_layout.removeWidget(graphics_view)
                    graphics_view.deleteLater()

                    # Create and add the matplotlib canvas
                    self.canvas = MatplotlibCanvas(self, width=8, height=6, dpi=100)
                    parent_layout.insertWidget(i, self.canvas)
                    break
        else:
            print("Warning: graphicsView not found in UI")

    def setup_connections(self):
        """Setup Qt signal connections"""
        # Connect buttons to their handlers
        add_button = self.findChild(QWidget, 'pushButton')
        if add_button:
            add_button.clicked.connect(self.on_add_step)

        edit_button = self.findChild(QWidget, 'pushButton_5')
        if edit_button:
            edit_button.clicked.connect(self.on_edit_step)

        delete_button = self.findChild(QWidget, 'pushButton_2')
        if delete_button:
            delete_button.clicked.connect(self.on_delete_step)

        recoater_button = self.findChild(QWidget, 'pushButton_4')
        if recoater_button:
            recoater_button.clicked.connect(self.on_recoater_settings)

        generate_button = self.findChild(QWidget, 'pushButton_3')
        if generate_button:
            generate_button.clicked.connect(self.on_generate_build_package)

    def on_add_step(self):
        """Handler for Add Step button"""
        print("Add Step clicked")
        # TODO: Implement add step dialog

    def on_edit_step(self):
        """Handler for Edit Step button"""
        print("Edit Step clicked")
        # TODO: Implement edit step dialog

    def on_delete_step(self):
        """Handler for Delete Step button"""
        print("Delete Step clicked")
        # TODO: Implement delete step functionality

    def on_recoater_settings(self):
        """Handler for Recoater Settings button"""
        print("Recoater Settings clicked")
        # TODO: Implement recoater dialog

    def on_generate_build_package(self):
        """Handler for Generate Build Package button"""
        print("Generate Build Package clicked")
        # TODO: Implement build package generation


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("OBP Yeah You Know Me")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
