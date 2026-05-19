import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
import screeninfo
from scipy import signal

monitor = 0
resolution = (1080, 1920)
x_max_list =[7, 14, 21 ,28, 36, 42]

class ImageDisplay(tk.Toplevel):
    def __init__(self, monitor: int):
        assert isinstance(monitor, int) and monitor >= 0, "Monitor must be a non-negative integer!"

        super().__init__()

        monitors = screeninfo.get_monitors()


        if len(monitors) <= monitor:
            raise Exception(f"Monitor index {monitor} is out of range. Found {len(monitors)} monitors.")

        # Select the specified monitor
        selected_monitor = monitors[monitor]
        self.width, self.height = selected_monitor.width, selected_monitor.height

        self.geometry(f"{self.width}x{self.height}+{selected_monitor.x}+{selected_monitor.y}")
        self.configure(background='black')

        self.overrideredirect(True)

        # Initialize the label to None
        self.label = None

    def show_image(self, image_object):
        assert isinstance(image_object, Image.Image), "Image must be a PIL Image object"

        photo = ImageTk.PhotoImage(image_object)

        if self.label is None:
            # Create a label to hold the image
            self.label = tk.Label(self, image=photo)
            self.label.image = photo  # Keep a reference to avoid garbage collection
            self.label.pack()
        else:
            self.__update_image(photo)

    def __update_image(self, photo):
        assert isinstance(photo, ImageTk.PhotoImage), "Image must be a PhotoImage object"

        # Update the image in the existing label
        self.label.configure(image=photo)
        self.label.image = photo  # Update the reference to avoid garbage collection

    class NoSecondMonitorError(Exception):
        pass

class App(tk.Tk):
    def __init__(self, monitor: int):
        super().__init__()
        self.image_display = ImageDisplay(monitor)

        self.protocol("WM_DELETE_WINDOW")

        img = tiled_sawtooth_pattern(x_max_list, resolution)

        self.image_display.show_image(img)

        self.mainloop()

def tiled_sawtooth_pattern(x_max_list, resolution: tuple[int, int]):
    assert len(x_max_list) == 6

    img_matrix = np.zeros(resolution, dtype=np.uint8)

    for i, x_max in enumerate(x_max_list):
        pattern_width = int(resolution[1] / 3)
        pattern_height = int(resolution[0] / 2)

        t = np.arange(pattern_width)
        omega = 2 * np.pi * (1 / x_max)
        waveform = (1 + signal.sawtooth(omega * t)) * 128

        pattern = np.tile(waveform, (pattern_height, 1))

        if i <= 2:
            start_height = 0
            stop_height = pattern_height
            start_width = i * pattern_width
            stop_width = start_width + pattern_width
        else:
            start_height = pattern_height
            stop_height = 2 * pattern_height
            start_width = (i - 3) * pattern_width
            stop_width = start_width + pattern_width

        img_matrix[start_height:stop_height, start_width:stop_width] = pattern

    return Image.fromarray(img_matrix)

App(monitor)