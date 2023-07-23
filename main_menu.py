import tkinter as tk
from tkinter import ttk
import subprocess
import sys
from ttkbootstrap import Style

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Traffic Simulator Main Menu")
        self.root.geometry("300x250")
        self.dark_mode = tk.BooleanVar(value=False)  # Set dark_mode to False by default
        self.setup_widgets()

    def setup_widgets(self):
        self.style = Style(theme="lumen")  # Choose the theme (other options: "flatly", "darkly", "united", etc.)

        label_heading = ttk.Label(self.root, text="Traffic Simulator Main Menu", font=("Helvetica", 16))
        label_heading.pack(pady=20)

        dark_mode_checkbox = ttk.Checkbutton(self.root, text="Dark Mode", variable=self.dark_mode, command=self.toggle_dark_mode)
        dark_mode_checkbox.pack(pady=5)

        button_gui = ttk.Button(self.root, text="Open GUI Version", command=self.open_gui)
        button_gui.pack(pady=10)

        button_command = ttk.Button(self.root, text="Open Command-Line Version", command=self.open_command)
        button_command.pack(pady=10)

    def toggle_dark_mode(self):
        theme = "lumen" if not self.dark_mode.get() else "darkly"  # Toggle between flatly (light) and darkly (dark) themes

        # Create a new ttkbootstrap.Style object with the desired theme and set it on the root and child widgets
        self.root.style = Style(theme=theme)
        for child in self.root.winfo_children():
            if isinstance(child, (ttk.Frame, ttk.Label, ttk.Button, ttk.Entry, ttk.Checkbutton, ttk.Combobox, ttk.Progressbar)):
                child.style = self.root.style

    def open_gui(self):
        self.root.destroy()
        subprocess.run([sys.executable, "main_gui.py"])

    def open_command(self):
        self.root.destroy()
        subprocess.run([sys.executable, "main.py"])


if __name__ == "__main__":
    root = tk.Tk()
    app = MainMenu(root)
    root.mainloop()
