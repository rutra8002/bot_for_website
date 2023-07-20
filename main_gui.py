import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import requests
import threading
import queue
from main import simulate_traffic, setup_logging
from ttkthemes import ThemedStyle


class TrafficSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Traffic Simulator")
        self.root.geometry("400x500")
        self.style = ThemedStyle(self.root)
        self.style.set_theme("arc")  # Choose the theme (other options: "plastik", "arc", "adapta", etc.)
        self.url_entry = ttk.Entry(self.root, width=40)
        self.num_requests_entry = ttk.Entry(self.root)
        self.retry_var = tk.IntVar()
        self.retry_var.set(1)
        self.speed_choice = tk.StringVar()
        self.choice_entry = ttk.Spinbox(self.root, from_=0, to=50, state=tk.DISABLED)
        self.choice2_entry = ttk.Spinbox(self.root, from_=0, to=50, state=tk.DISABLED)
        self.randomness_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, mode='determinate', length=300)
        self.start_button = ttk.Button(self.root, text="Start Simulation", command=self.start_simulation)
        self.is_simulation_running = False
        self.setup_gui()

    def setup_gui(self):
        label_url = ttk.Label(self.root, text="Enter the URL of the website to simulate traffic for:")
        label_url.pack(pady=10)
        self.url_entry.pack(pady=5)

        label_num_requests = ttk.Label(self.root, text="How many requests do you want to make?")
        label_num_requests.pack(pady=10)
        self.num_requests_entry.pack(pady=5)

        label_speed = ttk.Label(self.root, text="Select the connection speed:")
        label_speed.pack(pady=10)
        speed_choices = ["slow", "medium", "fast", "heck", "manual"]
        self.speed_choice.set(speed_choices[2])  # Default to "fast"
        speed_combobox = ttk.Combobox(self.root, values=speed_choices, state="readonly")
        speed_combobox.pack(pady=5)
        speed_combobox.set(speed_choices[2])  # Set default value

        label_choice = ttk.Label(self.root, text="Enter your choice (0-50):")
        self.choice_entry.pack(pady=5)

        label_choice2 = ttk.Label(self.root, text="Enter your choice2 (0-50):")
        self.choice2_entry.pack(pady=5)

        label_randomness = ttk.Label(self.root, text="How random would you like the connection time to be?")
        label_randomness.pack(pady=10)
        self.randomness_scale = tk.Scale(self.root, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL,
                                         length=200, variable=self.randomness_var, troughcolor="lightgray")
        self.randomness_scale.pack(pady=5)

        retry_checkbox = ttk.Checkbutton(self.root, text="Retry on failure", variable=self.retry_var, onvalue=1, offvalue=0)
        retry_checkbox.pack(pady=5)

        self.start_button.pack(pady=20)

        self.progress_bar.pack(pady=10)

        # Bind the event for when the speed choice is changed
        speed_combobox.bind("<<ComboboxSelected>>", self.speed_choice_changed)

    def lock_start_button(self):
        self.start_button.config(state=tk.DISABLED)

    def unlock_start_button(self):
        self.start_button.config(state=tk.NORMAL)

    def speed_choice_changed(self, event):
        speed_choice = self.speed_choice.get()
        if speed_choice == "manual":
            self.choice_entry.config(state=tk.NORMAL)
            self.choice2_entry.config(state=tk.NORMAL)
        else:
            self.choice_entry.delete(0, tk.END)  # Clear the entry fields
            self.choice2_entry.delete(0, tk.END)
            self.choice_entry.config(state=tk.DISABLED)
            self.choice2_entry.config(state=tk.DISABLED)

    def update_progress_bar(self, progress):
        self.progress_bar['value'] = progress
        self.root.update_idletasks()

    def show_error_message(self, message):
        messagebox.showerror("Error", message)

    def simulate_traffic_thread(self, url, num_requests, choice, choice2, randomness, retry_on_failure):
        try:
            for i in range(num_requests):
                progress = (i / num_requests) * 100
                self.queue.put(('progress', progress))
                simulate_traffic(url, 1, choice, choice2, randomness, retry_on_failure=bool(retry_on_failure))
        except Exception as e:
            self.queue.put(('error', str(e)))

        self.queue.put(('progress', 100))  # Ensure progress bar reaches 100%
        self.is_simulation_running = False
        self.unlock_start_button()

    def start_simulation(self):
        if self.is_simulation_running:
            return

        url = self.url_entry.get()
        num_requests = self.num_requests_entry.get()
        retry_on_failure = self.retry_var.get()

        if not url.strip() or not num_requests.strip():
            messagebox.showerror("Error", "URL and number of requests are required.")
            return

        try:
            num_requests = int(num_requests)
            if num_requests <= 0:
                raise ValueError("Number of requests must be greater than 0.")
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter a valid integer value.")
            return

        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                raise requests.exceptions.RequestException(f"Invalid URL: {url}")
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", f"Invalid URL or website is unreachable: {url}")
            return

        speed_choice = self.speed_choice.get()
        if speed_choice == "manual":
            try:
                choice = int(self.choice_entry.get())
                if choice < 0 or choice > 50:
                    raise ValueError("Choice must be between 0 and 50.")
                choice2 = int(self.choice2_entry.get())
                if choice2 < 0 or choice2 > 50:
                    raise ValueError("Choice2 must be between 0 and 50.")
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid input: {str(e)}")
                return
        else:
            if speed_choice == "slow":
                choice, choice2 = 20, 10
            elif speed_choice == "medium":
                choice, choice2 = 10, 5
            elif speed_choice == "fast":
                choice, choice2 = 5, 2.5
            elif speed_choice == "heck":
                choice, choice2 = 0, 0

        randomness = self.randomness_var.get()

        setup_logging()

        self.is_simulation_running = True
        self.lock_start_button()

        self.queue = queue.Queue()
        thread = threading.Thread(target=self.simulate_traffic_thread,
                                  args=(url, num_requests, choice, choice2, randomness, retry_on_failure))
        thread.daemon = True
        thread.start()

        self.update_progress_bar_thread()

    def update_progress_bar_thread(self):
        try:
            while self.is_simulation_running:
                item = self.queue.get(timeout=0.1)
                if item[0] == 'progress':
                    self.update_progress_bar(item[1])
                elif item[0] == 'error':
                    self.show_error_message(item[1])
                self.queue.task_done()
        except queue.Empty:
            if self.is_simulation_running:
                self.root.after(100, self.update_progress_bar_thread)


if __name__ == "__main__":
    root = tk.Tk()
    app = TrafficSimulatorApp(root)
    root.mainloop()
