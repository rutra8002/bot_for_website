import random
import time
import requests
import math

class ConnectionError(Exception):
    pass

def connect_with_proxy(url, proxy):
    proxies = {}
    try:
        response = requests.get(url, proxies=proxies, timeout=5)
        print(f"Connected to the website using proxy: {proxy}")
        print(f"Response status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"\033[31mFailed to connect to the website using proxy: {proxy}: {str(e)}\033[0m")
    except Exception as e:
        raise ConnectionError(f"\033[31mAn error occurred: {str(e)}\033[0m")

def simulate_traffic(url, num_requests, choice, choice2, randomness):
    times = 0

    with open('list.txt') as f:
        proxies = f.read().splitlines()

    for i in range(num_requests):
        print(f"\033[32mConnected to website {times} times.\033[0m")
        proxy = random.choice(proxies)
        try:
            connect_with_proxy(url, proxy)
            times += 1
        except ConnectionError as e:
            print(str(e))
            continue

        duration = randomisation(choice, randomness)
        disconnect_duration = randomisation(choice2, randomness)

        print(f"\033[33mStaying on the website for {duration} seconds...\033[0m")
        time.sleep(duration)

        print(f"\033[34mDisconnecting from the website for {disconnect_duration} seconds...\033[0m")
        time.sleep(disconnect_duration)

def randomisation(num, randomness):
    num += 1
    random_shit = (math.pi*math.e*math.sqrt(2)*math.tau/10) * randomness
    lowest_num = num - random_shit
    if lowest_num < 0:
        lowest_num = 0
    result = random.uniform(lowest_num, num + random_shit)
    result = abs(result -1)
    rounded_result = round(result, 2)
    return rounded_result

valid_choices = ["slow", "medium", "fast", "heck", "manual"]

while True:
    choice = input("How fast do you want to connect to the website? (slow, medium, fast, or manual): ")
    if choice == "manual":
        try:
            print("First choice is the average time of staying on the website, and choice2 is the average time of disconnecting from the website")
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

while True:
    try:
        randomness = float(input("How random would you like the connection time to be? (0 to 1): "))
        if 0 <= randomness <= 1:
            break
        else:
            print("Invalid input. Randomness must be between 0 and 1.")
    except ValueError:
        print("Invalid input. Please enter a valid float value between 0 and 1.")

url = 'http://www.rutra.live'
while True:
    try:
        num_requests = int(input("How many request do you want to make?"))
        break
    except ValueError:
        print("Invalid input")



simulate_traffic(url, num_requests, choice, choice2, randomness)
