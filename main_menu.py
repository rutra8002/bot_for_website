import tkinter as tk
from tkinter import ttk
import subprocess
import sys

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Traffic Simulator Main Menu")
        self.root.geometry("300x200")
        self.setup_widgets()

    def setup_widgets(self):
        label_heading = ttk.Label(self.root, text="Traffic Simulator Main Menu", font=("Helvetica", 16))
        label_heading.pack(pady=20)

        button_gui = ttk.Button(self.root, text="Open GUI Version", command=self.open_gui)
        button_gui.pack(pady=10)

        button_command = ttk.Button(self.root, text="Open Command-Line Version", command=self.open_command)
        button_command.pack(pady=10)

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
