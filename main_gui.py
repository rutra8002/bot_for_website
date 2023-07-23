import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import queue
from main import simulate_traffic, setup_logging, randomisation
from ttkbootstrap import Style
import time
from PIL import Image, ImageTk

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=self.text, justify="left", background="#ffffe0", relief="solid", borderwidth=1, wraplength=180)
        label.pack(ipadx=4)

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class TrafficSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Traffic Simulator")
        self.root.geometry("400x750")
        self.style = Style(theme="darkly")  # Choose the theme (other options: "flatly", "darkly", "united", etc.)
        self.setup_widgets()
        self.is_simulation_running = False
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_requests = 0
        self.avg_response_time = 0

        # Create a label to display real-time statistics
        self.stats_label = ttk.Label(self.root, text="")
        self.stats_label.pack(pady=10)

    def setup_widgets(self):
        self.create_theme_change_button()
        label_url = ttk.Label(self.root, text="Enter the URL of the website to simulate traffic for:")
        label_url.pack(pady=10)
        self.url_entry = ttk.Entry(self.root, width=40)
        self.url_entry.pack(pady=5)
        Tooltip(self.url_entry, "Enter the URL of the website you want to simulate traffic for.")

        label_num_requests = ttk.Label(self.root, text="How many requests do you want to make?")
        label_num_requests.pack(pady=10)
        self.num_requests_entry = ttk.Entry(self.root)
        self.num_requests_entry.pack(pady=5)
        Tooltip(self.num_requests_entry, "Enter the number of requests you want to simulate.")

        label_speed = ttk.Label(self.root, text="Select the connection speed:")
        label_speed.pack(pady=10)
        speed_choices = ["slow", "medium", "fast", "heck", "manual"]
        self.speed_choice = tk.StringVar(value=speed_choices[2])  # Default to "fast"
        speed_combobox = ttk.Combobox(self.root, values=speed_choices, state="readonly", textvariable=self.speed_choice)
        speed_combobox.pack(pady=5)
        Tooltip(speed_combobox, "Choose the connection speed for the simulation.\n'heck' and 'manual' options are for advanced users.")

        label_choice = ttk.Label(self.root, text="Enter your choice (0-50):")
        label_choice.pack(pady=5)
        self.choice_var = tk.DoubleVar(value=5)  # Default choice value for fast mode
        self.choice_entry = ttk.Spinbox(self.root, from_=0, to=50, increment=0.1, state=tk.DISABLED,
                                        textvariable=self.choice_var)
        self.choice_entry.pack(pady=5)
        Tooltip(self.choice_entry, "Enter the value for the first choice (0-50).\nOnly applicable for 'manual' connection speed.")

        label_choice2 = ttk.Label(self.root, text="Enter your choice2 (0-50):")
        label_choice2.pack(pady=5)
        self.choice2_var = tk.DoubleVar(value=2.5)  # Default choice2 value for fast mode
        self.choice2_entry = ttk.Spinbox(self.root, from_=0, to=50, increment=0.1, state=tk.DISABLED,
                                         textvariable=self.choice2_var)
        self.choice2_entry.pack(pady=5)
        Tooltip(self.choice2_entry, "Enter the value for the second choice (0-50).\nOnly applicable for 'manual' connection speed.")

        label_randomness = ttk.Label(self.root, text="How random would you like the connection time to be?")
        label_randomness.pack(pady=10)
        self.randomness_var = tk.DoubleVar()
        self.randomness_scale = ttk.Scale(
            self.root, from_=0, to=1, length=200, variable=self.randomness_var,
            style="TScale"
        )
        self.randomness_scale.pack(pady=5)
        Tooltip(self.randomness_scale, "Adjust the randomness level for connection time.\n0 means no randomness, 1 means fully random.")

        self.retry_var = tk.IntVar(value=1)
        retry_checkbox = ttk.Checkbutton(self.root, text="Retry on failure", variable=self.retry_var, onvalue=1,
                                         offvalue=0)
        retry_checkbox.pack(pady=5)
        Tooltip(retry_checkbox, "Enable this option to retry failed requests automatically.")

        self.validate_proxies_var = tk.IntVar(value=0)
        validate_proxies_checkbox = ttk.Checkbutton(self.root, text="Validate Proxies, (takes long time)",
                                                    variable=self.validate_proxies_var,
                                                    onvalue=1, offvalue=0)
        validate_proxies_checkbox.pack(pady=5)
        Tooltip(validate_proxies_checkbox, "Enable this option to validate proxies before using them for requests.")

        self.start_button = ttk.Button(self.root, text="Start Simulation", command=self.start_simulation)
        self.start_button.pack(pady=20)

        self.progress_bar = ttk.Progressbar(self.root, mode='determinate', length=300)
        self.progress_bar.pack(pady=10)
    def change_theme(self):
        selected_theme = self.theme_choice.get()
        self.style.theme_use(selected_theme)

    def create_theme_change_button(self):
        label_theme = ttk.Label(self.root, text="Select theme:")
        label_theme.pack(pady=10)

        theme_choices = ["flatly", "darkly", "united", "yeti", "cosmo", "lumen", "sandstone", "superhero", "solar", "cyborg", "vapor", "journal", "litera", "minty", "pulse", "morph", "simplex", "cerculean"]
        self.theme_choice = tk.StringVar(value="darkly")  # Default to "darkly"
        theme_combobox = ttk.Combobox(
            self.root, values=theme_choices, state="readonly", textvariable=self.theme_choice
        )
        theme_combobox.pack(pady=5)

        theme_button = ttk.Button(self.root, text="Change Theme", command=self.change_theme)
        theme_button.pack(pady=10)

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
            self.choice_entry.config(state=tk.DISABLED)
            self.choice2_entry.config(state=tk.DISABLED)

            # Set default values for choice and choice2 based on the selected speed
            if speed_choice == "slow":
                self.choice_var.set(20)
                self.choice2_var.set(10)
            elif speed_choice == "medium":
                self.choice_var.set(10)
                self.choice2_var.set(5)
            elif speed_choice == "fast":
                self.choice_var.set(5)
                self.choice2_var.set(2.5)
            elif speed_choice == "heck":
                self.choice_var.set(0)
                self.choice2_var.set(0)


    def update_progress_bar(self, progress):
        self.progress_bar['value'] = progress
        self.root.update_idletasks()

    def show_error_message(self, message):
        messagebox.showerror("Error", message)

    def update_statistics(self):
        stats_text = f"Total Requests: {self.total_requests} | " \
                     f"Avg Response Time: {self.avg_response_time:.2f} sec"

        self.stats_label.config(text=stats_text)

    def simulate_traffic_thread(self, url, num_requests, choice, choice2, randomness, retry_on_failure, validate_proxies):
        try:
            total_duration = 0.0
            for i in range(num_requests):
                start_time = time.time()
                try:
                    simulate_traffic(url, 1, choice, choice2, randomness, retry_on_failure=retry_on_failure,
                                     validate_proxies=validate_proxies)
                except ConnectionError:
                    pass  # Ignore failed requests for simplicity
                total_duration += (time.time() - start_time)
                self.total_requests += 1
                self.avg_response_time = total_duration / self.total_requests if self.total_requests > 0 else 0.0

                # Calculate progress based on the successful requests
                progress = (self.total_requests / num_requests) * 100
                # Convert progress to integer to ensure the progress bar reaches 100%
                progress = int(progress)

                # Update progress and statistics on the main thread using 'after'
                self.root.after(1, self.update_progress_bar, progress)
                self.root.after(1, self.update_statistics)

        except Exception as e:
            self.queue.put(('error', str(e)))

        self.is_simulation_running = False
        self.root.after(300, self.unlock_start_button)    # Delay before unlocking start button

    def start_simulation(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.avg_response_time = 0.0

        url = self.url_entry.get()
        num_requests = self.num_requests_entry.get()
        retry_on_failure = self.retry_var.get()
        validate_proxies = self.validate_proxies_var.get()

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
                choice = int(self.choice_var.get())
                if not 0 <= choice <= 50:
                    raise ValueError("Choice must be between 0 and 50.")
                choice2 = int(self.choice2_var.get())
                if not 0 <= choice2 <= 50:
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

        # Update statistics without actually starting the simulation
        total_duration = 0.0
        for i in range(num_requests):
            start_time = time.time()
            total_duration += randomisation(choice, randomness)
            total_duration += randomisation(choice2, randomness)
        avg_response_time = total_duration / (num_requests * 2) if num_requests > 0 else 0.0

        stats_text = f"Total Requests: {num_requests} | " \
                     f"Avg Response Time: {avg_response_time:.2f} sec"

        self.stats_label.config(text=stats_text)

        setup_logging()

        self.is_simulation_running = True
        self.lock_start_button()

        self.queue = queue.Queue()
        thread = threading.Thread(target=self.simulate_traffic_thread,
                                  args=(
                                      url, num_requests, choice, choice2, randomness, retry_on_failure,
                                      validate_proxies))
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