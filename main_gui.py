import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import queue
from main import simulate_traffic, setup_logging, randomisation
from ttkthemes import ThemedStyle
import time


class TrafficSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Traffic Simulator")
        self.root.geometry("400x500")
        self.style = ThemedStyle(self.root)
        self.style.set_theme("arc")  # Choose the theme (other options: "plastik", "arc", "adapta", etc.)
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
        label_url = ttk.Label(self.root, text="Enter the URL of the website to simulate traffic for:")
        label_url.pack(pady=10)
        self.url_entry = ttk.Entry(self.root, width=40)
        self.url_entry.pack(pady=5)

        label_num_requests = ttk.Label(self.root, text="How many requests do you want to make?")
        label_num_requests.pack(pady=10)
        self.num_requests_entry = ttk.Entry(self.root)
        self.num_requests_entry.pack(pady=5)

        label_speed = ttk.Label(self.root, text="Select the connection speed:")
        label_speed.pack(pady=10)
        speed_choices = ["slow", "medium", "fast", "heck", "manual"]
        self.speed_choice = tk.StringVar(value=speed_choices[2])  # Default to "fast"
        speed_combobox = ttk.Combobox(self.root, values=speed_choices, state="readonly", textvariable=self.speed_choice)
        speed_combobox.pack(pady=5)
        speed_combobox.bind("<<ComboboxSelected>>", self.speed_choice_changed)  # Bind the event

        label_choice = ttk.Label(self.root, text="Enter your choice (0-50):")
        label_choice.pack(pady=5)
        self.choice_var = tk.DoubleVar(value=5)  # Default choice value for fast mode
        self.choice_entry = ttk.Spinbox(self.root, from_=0, to=50, increment=0.1, state=tk.DISABLED,
                                        textvariable=self.choice_var)
        self.choice_entry.pack(pady=5)

        label_choice2 = ttk.Label(self.root, text="Enter your choice2 (0-50):")
        label_choice2.pack(pady=5)
        self.choice2_var = tk.DoubleVar(value=2.5)  # Default choice2 value for fast mode
        self.choice2_entry = ttk.Spinbox(self.root, from_=0, to=50, increment=0.1, state=tk.DISABLED,
                                         textvariable=self.choice2_var)
        self.choice2_entry.pack(pady=5)

        label_randomness = ttk.Label(self.root, text="How random would you like the connection time to be?")
        label_randomness.pack(pady=10)
        self.randomness_var = tk.DoubleVar()
        self.randomness_scale = tk.Scale(self.root, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL,
                                         length=200, variable=self.randomness_var, troughcolor="lightgray")
        self.randomness_scale.pack(pady=5)

        self.retry_var = tk.IntVar(value=1)
        retry_checkbox = ttk.Checkbutton(self.root, text="Retry on failure", variable=self.retry_var, onvalue=1,
                                         offvalue=0)
        retry_checkbox.pack(pady=5)

        self.validate_proxies_var = tk.IntVar(value=0)
        validate_proxies_checkbox = ttk.Checkbutton(self.root, text="Validate Proxies, (takes long time)",
                                                    variable=self.validate_proxies_var,
                                                    onvalue=1, offvalue=0)
        validate_proxies_checkbox.pack(pady=5)

        self.start_button = ttk.Button(self.root, text="Start Simulation", command=self.start_simulation)
        self.start_button.pack(pady=20)

        self.progress_bar = ttk.Progressbar(self.root, mode='determinate', length=300)
        self.progress_bar.pack(pady=10)

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

    def simulate_traffic_thread(self, url, num_requests, choice, choice2, randomness, retry_on_failure,
                                validate_proxies):
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

            # Fill the progress bar completely
            self.queue.put(('progress', 100))
            self.update_statistics()

        except Exception as e:
            self.queue.put(('error', str(e)))

        self.is_simulation_running = False
        self.root.after(300, self.unlock_start_button)  # Delay before unlocking start button

    def start_simulation(self):
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