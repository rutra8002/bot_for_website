import os
import random
import time
import requests
import math
import logging
from tqdm import tqdm
import webbrowser

class ConnectionError(Exception):
    pass

def is_proxy_valid(proxy):
    # Function to validate if a proxy is working properly
    try:
        response = requests.get("https://www.google.com", proxies={"http": proxy, "https": proxy}, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def connect_with_proxy(url, proxy, legit_mode=False, speed_choice=None):
    proxies = {"http": proxy, "https": proxy}
    try:
        if not legit_mode:
            response = requests.get(url, proxies=proxies, timeout=5)
            logging.info(f"Connected to the website using proxy: {proxy}")
            logging.info(f"Response status code: {response.status_code}")
        else:
            # Add a delay before opening the website in legit_mode
            if speed_choice == "slow":
                delay_before_opening = randomisation(20, 0.5)
            elif speed_choice == "medium":
                delay_before_opening = randomisation(10, 0.5)
            elif speed_choice == "fast":
                delay_before_opening = randomisation(5, 0.5)
            elif speed_choice == "heck":
                delay_before_opening = randomisation(0, 0.5)
            elif speed_choice == "manual":
                # You can use self.choice_var and self.choice2_var from the GUI
                # or hardcode the values based on the GUI input
                choice, choice2 = 5, 2.5
                delay_before_opening = randomisation(choice, 0.5)
            else:
                # Default to a delay of 5 seconds for unknown speed choices
                delay_before_opening = randomisation(5, 0.5)

            time.sleep(delay_before_opening)
            webbrowser.open(url)  # Open the website in the default web browser
            logging.info(f"Opened the website in the default web browser using proxy: {proxy}")

        return True
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to connect to the website using proxy: {proxy}: {str(e)}")
    except Exception as e:
        raise ConnectionError(f"An error occurred: {str(e)}")


def simulate_traffic(url, num_requests, choice, choice2, randomness, retry_on_failure=True, validate_proxies=False, legit_mode=False):
    times = 0
    successful_requests = 0

    with open('list.txt') as f:
        proxies = f.read().splitlines()

    valid_proxies = proxies if not validate_proxies else [proxy for proxy in proxies if is_proxy_valid(proxy)]

    if validate_proxies and not valid_proxies:
        raise ConnectionError("No valid proxies found. Please check your proxy list or disable proxy validation.")

    for i in tqdm(range(num_requests), desc="Simulating Traffic", unit="request", bar_format="{l_bar}{bar}|"):
        if retry_on_failure:
            connected = False
            while not connected:
                logging.info(f"Connected to website {successful_requests} times.")
                proxy = random.choice(valid_proxies)
                try:
                    connect_with_proxy(url, proxy, legit_mode)
                    times += 1
                    successful_requests += 1
                    connected = True

                    duration = randomisation(choice, randomness)
                    disconnect_duration = randomisation(choice2, randomness)

                    logging.info(f"Staying on the website for {duration:.2f} seconds...")
                    time.sleep(duration)

                    logging.info(f"Disconnecting from the website for {disconnect_duration:.2f} seconds...")
                    time.sleep(disconnect_duration)

                except ConnectionError as e:
                    logging.error(str(e))
                    if not retry_on_failure:
                        break
        else:
            logging.info(f"Connected to website {successful_requests} times.")
            proxy = random.choice(valid_proxies)
            try:
                connect_with_proxy(url, proxy, legit_mode)
                times += 1
                successful_requests += 1

                duration = randomisation(choice, randomness)
                disconnect_duration = randomisation(choice2, randomness)

                logging.info(f"Staying on the website for {duration:.2f} seconds...")
                time.sleep(duration)

                logging.info(f"Disconnecting from the website for {disconnect_duration:.2f} seconds...")
                time.sleep(disconnect_duration)

            except ConnectionError as e:
                logging.warning(str(e))
                if not retry_on_failure:
                    break


def randomisation(num, randomness):
    num += 1
    random_shit = (math.pi * math.e * math.sqrt(2) * math.tau / 10) * randomness / 2
    lowest_num = num - random_shit
    if lowest_num < 0:
        lowest_num = 0
    result = random.uniform(lowest_num, num + random_shit)
    result = abs(result - 1)
    rounded_result = round(result, 2)
    return rounded_result


def get_user_choices():
    valid_choices = ["slow", "medium", "fast", "heck", "manual"]
    while True:
        choice = input("How fast do you want to connect to the website? (slow, medium, fast, or manual): ")
        if choice == "manual":
            try:
                print(
                    "First choice is the average time of staying on the website, and choice2 is the average time of "
                    "disconnecting from the website")

                choice = int(input("Enter your choice (0-50): "))
                if choice < 0 or choice > 50:
                    raise ValueError("Choice must be between 0 and 50.")
                choice2 = int(input("Enter your choice2 (0-50): "))
                if choice2 < 0 or choice2 > 50:
                    raise ValueError("Choice2 must be between 0 and 50.")
                break
            except ValueError as e:
                print(f"Invalid input: {str(e)}")
        else:
            if choice in valid_choices:
                if choice == "slow":
                    choice, choice2 = 20, 10
                elif choice == "medium":
                    choice, choice2 = 10, 5
                elif choice == "fast":
                    choice, choice2 = 5, 2.5
                elif choice == "heck":
                    choice, choice2 = 0, 0
                break
            else:
                print("Invalid choice.")
    return choice, choice2


def get_randomness():
    while True:
        try:
            randomness = float(input("How random would you like the connection time to be? (0 to 1): "))
            if 0 <= randomness <= 1:
                break
            else:
                print("Invalid input. Randomness must be between 0 and 1.")
        except ValueError:
            print("Invalid input. Please enter a valid float value between 0 and 1.")
    return randomness


def setup_logging():
    # Create the 'logs' folder if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Get the current date and time to use in the log file name
    current_datetime = time.strftime("%Y-%m-%d_%H-%M-%S")
    log_file = f"logs/traffic_simulation_{current_datetime}.log"

    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_user_input():
    url = input("Enter the URL of the website to simulate traffic for: ")

    while True:
        try:
            num_requests = int(input("How many requests do you want to make? "))
            if num_requests > 0:
                break
            else:
                print("Number of requests must be greater than 0.")
        except ValueError:
            print("Invalid input. Please enter a valid integer value.")

    legit_mode = input("Do you want to use legit mode? (y/n): ").lower().startswith("y")

    return url, num_requests, legit_mode

if __name__ == "__main__":
    url, num_requests, legit_mode = get_user_input()
    choice, choice2 = get_user_choices()
    randomness = get_randomness()

    # Call the simulate_traffic function with the provided legit_mode flag
    simulate_traffic(url, num_requests, choice, choice2, randomness, retry_on_failure=True, legit_mode=legit_mode)