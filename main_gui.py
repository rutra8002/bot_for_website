import tkinter as tk
from tkinter import messagebox
from main import simulate_traffic, setup_logging


class TrafficSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Traffic Simulator")
        self.root.geometry("400x350")
        self.url_entry = tk.Entry(self.root, width=40)
        self.num_requests_entry = tk.Entry(self.root)
        self.retry_var = tk.IntVar()
        self.retry_var.set(1)
        self.speed_choice = tk.StringVar()
        self.randomness_scale = tk.Scale(self.root, from_=0, to=1, resolution=0.1, orient=tk.HORIZONTAL, length=200)
        self.setup_gui()

    def setup_gui(self):
        label_url = tk.Label(self.root, text="Enter the URL of the website to simulate traffic for:")
        label_url.pack(pady=10)
        self.url_entry.pack(pady=5)

        label_num_requests = tk.Label(self.root, text="How many requests do you want to make?")
        label_num_requests.pack(pady=10)
        self.num_requests_entry.pack(pady=5)

        label_speed = tk.Label(self.root, text="Select the connection speed:")
        label_speed.pack(pady=10)
        speed_choices = ["slow", "medium", "fast", "heck", "manual"]
        self.speed_choice.set(speed_choices[2])  # Default to "fast"
        speed_menu = tk.OptionMenu(self.root, self.speed_choice, *speed_choices)
        speed_menu.pack(pady=5)

        label_randomness = tk.Label(self.root, text="How random would you like the connection time to be?")
        label_randomness.pack(pady=10)
        self.randomness_scale.pack(pady=5)

        retry_checkbox = tk.Checkbutton(self.root, text="Retry on failure", variable=self.retry_var, onvalue=1, offvalue=0)
        retry_checkbox.pack(pady=5)

        start_button = tk.Button(self.root, text="Start Simulation", command=self.start_simulation)
        start_button.pack(pady=20)

    def start_simulation(self):
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

        speed_choice = self.speed_choice.get()
        if speed_choice == "manual":
            try:
                choice = int(input("Enter your choice (0-50): "))
                if choice < 0 or choice > 50:
                    raise ValueError("Choice must be between 0 and 50.")
                choice2 = int(input("Enter your choice2 (0-50): "))
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

        randomness = self.randomness_scale.get()

        setup_logging()

        try:
            simulate_traffic(url, num_requests, choice, choice2, randomness, retry_on_failure=bool(retry_on_failure))
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        messagebox.showinfo("Simulation Complete", "Traffic simulation completed successfully.")


if __name__ == "__main__":
    root = tk.Tk()
    app = TrafficSimulatorApp(root)
    root.mainloop()
