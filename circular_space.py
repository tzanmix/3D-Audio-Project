import tkinter as tk
import math

class PieSlice:
    def __init__(self, canvas, center, radius, start_angle, extent, color, degree, callback):
        self.canvas = canvas
        self.center = center
        self.radius = radius
        self.start_angle = start_angle
        self.extent = extent
        self.degree = degree
        self.id = canvas.create_arc(
            center[0] - radius, center[1] - radius,
            center[0] + radius, center[1] + radius,
            start=start_angle, extent=extent,
            fill=color, outline='black'
        )
        canvas.tag_bind(self.id, '<Button-1>', lambda event: callback(degree))

        # Calculate label position
        mid_angle_rad = math.radians((start_angle + extent / 2))
        label_x = center[0] + (radius / 2) * math.cos(mid_angle_rad)
        label_y = center[1] - (radius / 2) * math.sin(mid_angle_rad)

        # Display degree label
        canvas.create_text(label_x, label_y, text=str(degree)+'°', fill='black', font=('Arial', 12, 'bold'))

class PieChartApp:
    def __init__(self, root, label_var, slices=24):
        self.root = root
        self.canvas = tk.Canvas(root, width=400, height=400, bg='white')
        self.canvas.pack()
        self.center = (200, 200)
        self.radius = 300
        self.slices = slices
        self.selected_degree = 0
        self.selected_label_var = label_var

        self.draw_pie()

    def draw_pie(self):
        angle_per_slice = 360 / self.slices
        for i in range(self.slices):
            start_angle = -90 - i * angle_per_slice #0 degress on top
            raw_degree = -180 + i * angle_per_slice
            degree = round(raw_degree / 5) * 5
            PieSlice(
                self.canvas,
                self.center,
                self.radius,
                start_angle = start_angle,
                extent = - angle_per_slice, #clockwise direction
                color = 'white',
                degree = degree,
                callback = self.on_slice_click
            )

    def on_slice_click(self, degree):
        self.selected_degree = degree
        print(f"Selected: {self.selected_degree}°")
        self.selected_label_var.set(degree)

    def get_selected_azimuth(self):
        print(f"You selected {self.selected_degree}")
        return self.selected_degree


# if __name__ == '__main__':
#     root = tk.Tk()
#     root.title("Clickable Pie Chart")
#     app = PieChartApp(root)
#     root.mainloop()
    
