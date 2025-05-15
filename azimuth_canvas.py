import tkinter as tk
import math

class PieSlice:
    def __init__(self, canvas, center, radius, start_angle, extent, color, degree, callback, app_ref):
        self.canvas = canvas
        self.color = color
        self.center = center
        self.radius = radius
        self.start_angle = start_angle
        self.extent = extent
        self.degree = degree
        self.id = canvas.create_arc(
            center[0] - radius, center[1] - radius,
            center[0] + radius, center[1] + radius,
            start=start_angle, extent=extent,
            fill=color, outline='white'
        )
        self.highlight_color = "#bd20a3"
        self.selected_color = "#701a62"
        self.app_ref = app_ref  # Reference to parent app
        # Event bindings
        canvas.tag_bind(self.id, "<Enter>", self.on_hover)
        canvas.tag_bind(self.id, "<Leave>", self.on_leave)
        canvas.tag_bind(self.id, "<Button-1>", lambda event: callback(degree, self))

        # Calculate label position
        mid_angle_rad = math.radians((start_angle + extent / 2))
        label_x = center[0] + (radius / 2) * math.cos(mid_angle_rad)
        label_y = center[1] - (radius / 2) * math.sin(mid_angle_rad)

        # Display degree label
        canvas.create_text(label_x, label_y, text=str(degree)+'°', fill='white', font=('Arial', 12, 'bold'))

    def on_hover(self, event):
            if self.app_ref.selected_slice != self:
                self.canvas.itemconfig(self.id, fill=self.highlight_color)

    def on_leave(self, event):
        if self.app_ref.selected_slice != self:
            self.canvas.itemconfig(self.id, fill=self.color)

    def highlight(self):
        self.canvas.itemconfig(self.id, fill=self.selected_color)

    def unhighlight(self):
        self.canvas.itemconfig(self.id, fill=self.color)

class PieChartApp:
    def __init__(self, root, label_var, slices=24):
        self.root = root
        self.canvas = tk.Canvas(root, width=400, height=400, bg='white')
        self.canvas.pack()
        self.center = (200, 200)
        self.radius = 300
        self.slices = slices
        self.selected_degree = 0
        self.selected_slice = None
        self.selected_label_var = label_var

        self.draw_pie()

    def draw_pie(self):
        angle_per_slice = 360 / self.slices
        for i in range(self.slices):
            
            raw_degree = -180 + i * angle_per_slice
            degree = round(raw_degree / 5) * 5
            center_angle = - raw_degree + 105
            start_angle = center_angle - angle_per_slice/2
            PieSlice(
                self.canvas,
                self.center,
                self.radius,
                start_angle = start_angle,
                extent = - angle_per_slice, #clockwise direction
                color = '#23272D',
                degree = degree,
                callback = self.on_slice_click,
                app_ref = self
            )

    def on_slice_click(self, degree, slice_obj):
        # Unhighlight previous
        if self.selected_slice:
            self.selected_slice.unhighlight()

        self.selected_degree = degree
        self.selected_slice = slice_obj
        self.selected_slice.highlight()

        print(f"Selected: {self.selected_degree}°")
        self.selected_label_var.set(degree)

    def get_selected_azimuth(self):
        print(f"You selected {self.selected_degree}")
        return self.selected_degree


    
