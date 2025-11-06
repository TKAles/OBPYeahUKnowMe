# OBP Yeah You Know Me

3D Additive Manufacturing Build Package Generator for OpenMelt based systems.

**WARNING:** AI assisted/generated code is present in this repository. Mainly for UI and other boring tasks. If you are philoshopically opposed to this run away now. **HERE BE DRAGONS**

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

## Installation

1. Install Python 3.8 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python __main__.py
```

## Architecture

The application consists of:
- `__main__.py`: Main application file with matplotlib canvas integration
- `v0_yeahobpuknowme.ui`: Qt Designer UI file for the main window
- `v0_recoater_dialog.ui`: Qt Designer UI file for recoater settings dialog

## 3D Visualization
Matplotlib based visualization.  

## License
MIT License unless otherwise specifically noted.
See LICENSE file for details.
