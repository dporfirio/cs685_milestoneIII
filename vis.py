"""
NOTE: Students should not need to modify this file.

This file contains GUI visualization code. 
"""
import random
import time
import tkinter as tk
from tkinter import font as tkfont
from tkinter.scrolledtext import ScrolledText


class Map:

    def __init__(self):
        """
        Initialize everything, including GUI resolution and different GUI panes.
        This is done for you --- no interaction with this method needed.
        """
        self.window = tk.Tk()
        self.window.title("Visualization")
        self.window.geometry("890x480")
        self.plan_output = ScrolledText(self.window, wrap="word", state="disabled")
        self.plan_output_font = tkfont.Font(font=self.plan_output.cget("font"))
        font_size = self.plan_output_font.cget("size")
        pixel_size = (
            font_size * self.window.winfo_fpixels("1p")
            if font_size > 0 else -font_size
        )
        self.plan_output_font.configure(size=-max(1, round(pixel_size) - 2))
        self.plan_output.configure(font=self.plan_output_font)
        self.plan_output.place(x=640, y=48, width=250, height=384)
        self.grid_size = (0,0)
        self.obstacles = set()

    def show(self) -> None:
        """
        Show the GUI.
        No interaction with this method needed.
        """
        self.window.mainloop()

    def get_pixels(self) -> list[bytearray]:
        """
        Return 0.8*480 rows of 0.8*640 grayscale pixels; zero denotes black.
        No interaction with this method needed.
        """
        width, height = 512, 384
        columns, rows = self.grid_size
        if columns <= 0 or rows <= 0:
            raise ValueError("Set the grid before reading pixels")
        pixels = [bytearray([255]) * width for _ in range(height)]
        x_edges = [int(column * (width - 1) / columns + 0.5)
                   for column in range(columns + 1)]
        y_edges = [int(row * (height - 1) / rows + 0.5)
                   for row in range(rows + 1)]
        # Draw the grid first so obstacles cover shared grid lines.
        for y in y_edges:
            pixels[y][:] = bytes([211]) * width
        for values in pixels:
            for x in x_edges:
                values[x] = 211
        for column, row in self.obstacles:
            left, right = x_edges[column:column + 2]
            black = bytes(right - left)
            for y in range(y_edges[row], y_edges[row + 1]):
                pixels[y][left:right] = black
        return pixels

    def set_grid(self, x: int, y: int) -> None:
        """
        A grid is basically for drawing the obstacles.
        No interaction with this method will be needed.
        """
        if x <= 0 or y <= 0:
            raise ValueError("Grid dimensions must be positive")

        self.grid_size = (x, y)
        self.obstacles.clear()

        if hasattr(self, "canvas"):
            self.canvas.destroy()
        self.canvas = tk.Canvas(self.window, highlightthickness=0)
        self.canvas.place(x=64, y=48, width=512, height=384)

        def draw_grid(event):
            self.canvas.delete("all")
            width, height = event.width - 1, event.height - 1
            for column in range(x + 1):
                position = column * width / x
                self.canvas.create_line(position, 0, position, height, fill="light grey")
            for row in range(y + 1):
                position = row * height / y
                self.canvas.create_line(0, position, width, position, fill="light grey")

            self._draw_obstacles(width, height)
            self.draw_locations()

        self.canvas.bind("<Configure>", draw_grid)
        print("drawn grid")

    def draw_locations(self) -> None:
        """
        Draw the locations of entities in C Space.
        No interaction with this method needed.
        """
        self.canvas.delete("location")
        width = self.canvas.winfo_width() - 1
        height = self.canvas.winfo_height() - 1
        if width <= 0 or height <= 0:
            return
        executor = getattr(self, "executor", None)
        for name, coordinates in getattr(self, "locations", {}).items():
            pixel_x, pixel_y = coordinates[:2]
            x, y = pixel_x * width / 511, pixel_y * height / 383
            objects = [
                object_name for object_name in ("cake", "cube")
                if getattr(self, object_name, None) == name
            ]
            label = f"{name} ({', '.join(objects)})" if objects else name
            if executor is not None:
                label = self.location_label(name)
            self.canvas.create_oval(
                x - 3, y - 3, x + 3, y + 3,
                fill="green", outline="green", tags="location",
            )
            on_right = x <= width / 2
            self.canvas.create_text(
                x + 6 if on_right else x - 6,
                max(8, min(y, height - 8)),
                text=label, fill="red", anchor="w" if on_right else "e",
                font=("TkDefaultFont", 8), tags="location",
            )

        if executor is not None:
            self.draw_robot()

    def _item_label(self, item):
        """
        Internal method for labeling items.
        """
        contents = [self._item_label(child) for child, parent in self.executor.contained.items()
                    if parent == item]
        return f"{item} containing {', '.join(contents)}" if contents else item

    def location_label(self, name):
        """
        Internal method for labeling locations.
        """
        items = [self._item_label(item) for item in self.executor.item_locations
                 if getattr(self, item) == name]
        items.extend(f"{self._item_label(item)} portaled" for item in sorted(self.executor.portaled)
                     if self.executor.item_locations[item] == name)
        if name in self.executor.active_portals:
            items.append("active")
        return f"{name} ({', '.join(items)})" if items else name

    def draw_robot(self):
        """
        Internal method for drawing and labeling the robot.
        """
        canvas = self.canvas
        canvas.delete("robot")
        width, height = canvas.winfo_width() - 1, canvas.winfo_height() - 1
        if width <= 0 or height <= 0:
            return
        px, py, _ = self.executor.robot_position
        x, y = px * width / 511, py * height / 383
        canvas.create_oval(x - 5, y - 5, x + 5, y + 5,
                           fill="blue", outline="blue", tags="robot")
        label = "Robot"
        if self.executor.held:
            label += f" (holding {self._item_label(self.executor.held)})"
        canvas.create_text(x + 7 if x <= width / 2 else x - 7,
                           max(8, min(y + 14, height - 8)), text=label,
                           anchor="w" if x <= width / 2 else "e",
                           fill="dark blue", font=("TkDefaultFont", 8), tags="robot")

    def process_events(self, force=False):
        """
        This method refreshes the visualizer.
        If you decide to visualize RRT/RRT*, you can use this to refresh the window.
        We want to keep Tk responsive, so we throttle routine calls to once every 50 ms.
        """
        if not force and time.monotonic() - getattr(self, "_last_update", 0) < 0.05:
            return
        self.window.update()
        if not self.window.winfo_exists():
            raise SystemExit
        self._last_update = time.monotonic()

    def start_execution(self):
        """
        Initialize the visualization of plan execution.
        This is done for you already in exec.py.
        """
        output = self.plan_output
        self.action_font = tkfont.Font(font=output.cget("font"))
        self.action_font.configure(weight="bold")
        output.tag_configure("current_action", foreground="blue", font=self.action_font)
        self.advance = tk.BooleanVar(master=self.window)
        self.console_message = tk.StringVar(master=self.window)
        self.output_height = output.place_info()["height"]
        output.place_configure(height=int(self.output_height) - 30)
        self.console = tk.Label(self.window, textvariable=self.console_message,
                                anchor="w", relief="sunken", borderwidth=1)
        self.console.place(in_=output, relx=0, rely=1, y=4, relwidth=1, height=24)

        def next_action():
            self.console_message.set("")
            self.advance.set(True)

        self.next_button = tk.Button(self.window, text="Next", command=next_action)
        self.next_button.place(relx=1, rely=1, x=-10, y=-10, anchor="se")
        self.next_button.bind("<Destroy>", lambda event: self.advance.set(True))
        self.wait_for_next_action()

    def begin_action(self, index):
        """
        Update the visualization when a plan action is selected. This is done for you.
        """
        self.next_button.configure(state="disabled")
        self.plan_output.tag_remove("current_action", "1.0", "end")
        line = index + 3
        self.plan_output.tag_add("current_action", f"{line}.0", f"{line}.end")
        self.plan_output.see(f"{line}.0")
        self.clear_paths()

    def wait_for_next_action(self):
        """
        Internal method.
        """
        self.window.update_idletasks()
        self.advance.set(False)
        self.next_button.configure(state="normal")
        self.window.wait_variable(self.advance)
        if not self.window.winfo_exists():
            raise SystemExit

    def show_message(self, message):
        """
        Console logs. No interaction with this method needed.
        """
        self.console_message.set(message)

    def finish_execution(self):
        """
        Update the visualizer when the plan has finished executing.
        This is already done for you in exec.py
        """
        self.next_button.destroy()
        self.console.destroy()
        self.plan_output.place_configure(height=self.output_height)
        self.plan_output.tag_remove("current_action", "1.0", "end")
        self.clear_paths()

    def clear_paths(self):
        """
        Use this to clear path and tree visualizations (eg., after execution is finished)
        """
        self.canvas.delete("rrt_path")
        self.canvas.delete("rrt_tree")

    def draw_path(self, path):
        """
        Exec already calls this method once an RRT/RRT* path is found.
        No interaction with this method needed.
        """
        width = self.canvas.winfo_width() - 1
        height = self.canvas.winfo_height() - 1
        points = [(x * width / 511, y * height / 383) for x, y in path]
        if len(points) > 1:
            self.canvas.create_line(*[v for point in points for v in point],
                                    fill="red", tags="rrt_path")
        for x, y in points:
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3,
                                    fill="red", outline="red", tags="rrt_path")

    def randomly_generate_obstacles(self, growth_factor: int = 5) -> None:
        """
        Obstacle randomizer.
        No interaction with this method needed.
        """
        x, y = self.grid_size
        if x <= 0 or y <= 0:
            return
        self.obstacles = set()
        target = x * y // 5
        while len(self.obstacles) <= target:
            column, row = random.randrange(x), random.randrange(y)
            growth_x = random.randint(0, growth_factor)
            growth_y = random.randint(0, growth_factor)
            self.obstacles.update(
                (grown_column, grown_row)
                for grown_column in range(max(0, column - growth_x),
                                          min(x, column + growth_x + 1))
                for grown_row in range(max(0, row - growth_y),
                                       min(y, row + growth_y + 1))
            )

        self._draw_obstacles(
            self.canvas.winfo_width() - 1, self.canvas.winfo_height() - 1
        )

    def _draw_obstacles(self, width: int, height: int) -> None:
        """
        Internal helper for drawing obstacles.
        """
        self.canvas.delete("obstacle")
        x, y = self.grid_size
        cell_width, cell_height = width / x, height / y
        for column, row in self.obstacles:
            self.canvas.create_rectangle(
                column * cell_width, row * cell_height,
                (column + 1) * cell_width, (row + 1) * cell_height,
                fill="black", outline="", tags="obstacle",
            )
        self.canvas.tag_raise("location")
