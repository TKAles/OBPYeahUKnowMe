"""
3D visualization component for build steps using matplotlib
"""

import math

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


class Build3DVisualizer(FigureCanvas):
    """3D visualizer for build steps using matplotlib"""

    def __init__(self, parent=None):
        self.canvas = FigureCanvas()
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas.figure = self.figure
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

        colors = ['gold', 'lightgreen', 'lightblue', 'lightcoral', 'plum', 'orange']

        # Collect all polygons with their z-order for proper rendering
        all_polygons = []
        max_z = 0  # Track maximum Z height for axis limits

        for step_index, build_step in enumerate(build_steps):
            color = colors[step_index % len(colors)]
            dims = build_step.dimensions

            # Get position offsets from build step
            x_offset = build_step.x_offset
            y_offset = build_step.y_offset

            # Calculate starting Z based on starting layer
            current_z = build_step.starting_layer * layer_height

            # Create each repetition
            for rep in range(build_step.repetitions):
                z_offset = current_z + (layer_height / 2)

                if build_step.shape_type == "square":
                    size = dims.get("size", 10)
                    faces = self.create_box_vertices(size, size, layer_height, x_offset, y_offset, z_offset)
                    poly3d = Poly3DCollection(faces, facecolor=color, edgecolor='black',
                                             linewidths=0.5, alpha=0.9)
                    poly3d.set_sort_zpos(z_offset)
                    all_polygons.append((z_offset, poly3d))

                elif build_step.shape_type == "rectangle":
                    width = dims.get("width", 10)
                    length = dims.get("length", 15)
                    faces = self.create_box_vertices(width, length, layer_height, x_offset, y_offset, z_offset)
                    poly3d = Poly3DCollection(faces, facecolor=color, edgecolor='black',
                                             linewidths=0.5, alpha=0.9)
                    poly3d.set_sort_zpos(z_offset)
                    all_polygons.append((z_offset, poly3d))

                elif build_step.shape_type == "circle":
                    diameter = dims.get("diameter", 10)
                    radius = diameter / 2
                    faces = self.create_cylinder_faces(radius, layer_height, 16, x_offset, y_offset, z_offset)
                    poly3d = Poly3DCollection(faces, facecolor=color, edgecolor='black',
                                             linewidths=0.5, alpha=0.9)
                    poly3d.set_sort_zpos(z_offset)
                    all_polygons.append((z_offset, poly3d))

                elif build_step.shape_type == "ellipse":
                    width = dims.get("width", 10)
                    length = dims.get("length", 15)
                    # Use larger radius and scale for ellipse
                    radius = max(width, length) / 2
                    faces = self.create_cylinder_faces(radius, layer_height, 24, x_offset, y_offset, z_offset)

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

                    poly3d = Poly3DCollection(scaled_faces, facecolor=color, edgecolor='black',
                                             linewidths=0.5, alpha=0.9)
                    poly3d.set_sort_zpos(z_offset)
                    all_polygons.append((z_offset, poly3d))

                current_z += layer_height
                max_z = max(max_z, current_z)

        # Add polygons in order from bottom to top for correct z-sorting
        for z_pos, poly3d in sorted(all_polygons, key=lambda x: x[0]):
            self.ax.add_collection3d(poly3d)

        # Set axis limits and aspect ratio
        if build_steps:
            max_dim = 0
            max_x_extent = 0
            max_y_extent = 0

            for build_step in build_steps:
                dims = build_step.dimensions
                x_off = abs(build_step.x_offset)
                y_off = abs(build_step.y_offset)

                if build_step.shape_type == "square":
                    size = dims.get("size", 10)
                    max_dim = max(max_dim, size)
                    max_x_extent = max(max_x_extent, x_off + size / 2)
                    max_y_extent = max(max_y_extent, y_off + size / 2)
                elif build_step.shape_type in ["rectangle", "ellipse"]:
                    width = dims.get("width", 10)
                    length = dims.get("length", 15)
                    max_dim = max(max_dim, width, length)
                    max_x_extent = max(max_x_extent, x_off + width / 2)
                    max_y_extent = max(max_y_extent, y_off + length / 2)
                elif build_step.shape_type == "circle":
                    diameter = dims.get("diameter", 10)
                    max_dim = max(max_dim, diameter)
                    max_x_extent = max(max_x_extent, x_off + diameter / 2)
                    max_y_extent = max(max_y_extent, y_off + diameter / 2)

            # Set limits with some padding
            x_limit = max_x_extent * 1.2
            y_limit = max_y_extent * 1.2
            self.ax.set_xlim([-x_limit, x_limit])
            self.ax.set_ylim([-y_limit, y_limit])
            self.ax.set_zlim([0, max_z * 1.1])

        # Set viewing angle
        self.ax.view_init(elev=30, azim=45)
        self.draw()
