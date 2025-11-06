# OBP Yeah You Know Me

3D Additive Manufacturing Build Package Generator for OpenMelt based systems.

WARNING: AI assisted/generated code is present in this repository. Mainly for UI and other boring tasks. If you are philoshopically opposed to this run away now.

## Overview

This application provides a GUI for configuring and generating build packages for 3D additive manufacturing processes. It features a 3D visualization of the build volume and allows users to configure beam parameters, build sequences, and recoater settings.

## Features

- **3D Build Volume Visualization**: Real-time 3D visualization using matplotlib showing:
  - Build platform
  - Coordinate system (X, Y, Z axes)
  - Build volume boundaries
  - Default viewing angle optimized for clarity

- **Beam Parameters Configuration**:
  - Beam spot size (microns)
  - Beam power (Watts)

- **Build Sequence Management**:
  - Add, edit, and delete build steps
  - List view of current build sequence

- **Recoater Settings**: Access to recoater blade configuration

- **Build Options**:
  - Heat balance
  - Jump safe
  - Splatter safe
  - Triggered start

## Installation

1. Install Python 3.8 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

## Architecture

The application consists of:
- `main.py`: Main application file with matplotlib canvas integration
- `v0_yeahobpuknowme.ui`: Qt Designer UI file for the main window
- `v0_recoater_dialog.ui`: Qt Designer UI file for recoater settings dialog

### Key Components

- **MatplotlibCanvas**: Custom widget that replaces the QGraphicsView with a matplotlib FigureCanvas
- **MainWindow**: Main application window that loads the UI and sets up the 3D visualization

## 3D Visualization

The default 3D view shows:
- A gray build platform at Z=0
- Red, green, and blue arrows indicating X, Y, and Z axes respectively
- Dashed lines showing the build volume boundaries
- Default viewing angle: elevation=20°, azimuth=45°
- Coordinate ranges: X=[-60,60]mm, Y=[-60,60]mm, Z=[0,120]mm

## Development

To modify the UI, edit the `.ui` files using Qt Designer and reload the application.

## License

See LICENSE file for details.
