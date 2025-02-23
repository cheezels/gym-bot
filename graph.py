import matplotlib.pyplot as plt
import numpy as np
import json
from datetime import datetime, timedelta
from collections import defaultdict

def process_data(capacity_json):
    with open(capacity_json, 'r') as file:
        try:
            input_data = json.load(file)
            print(input_data)
        except json.JSONDecodeError as e:
            print(f"Error loading JSON: {e}")

    one_month_ago = datetime.now() - timedelta(days=30)
    today_weekday = datetime.now().weekday()

    # Function to filter records within the last month
    def is_within_last_month(item):
        try:
            item_date = datetime.strptime(item["Time_in"], "%Y-%m-%d %H:%M:%S")  # Adjust format if needed
            return item_date >= one_month_ago
        except (KeyError, ValueError):
            return False  # Skip items with missing or invalid dates

    # Function to filter records that fall on the same day of the week as today
    def is_same_weekday(item):
        try:
            item_date = datetime.strptime(item["Time_in"], "%Y-%m-%d %H:%M:%S")
            return item_date.weekday() == today_weekday
        except (KeyError, ValueError):
            return False

    # Apply both filters
    filtered_data = [item for item in input_data if is_within_last_month(item) and is_same_weekday(item)]
    print(filtered_data)

    # Initialize a dictionary to count entries per hour range
    time_slots = defaultdict(int)

    # Check how many entries are active in each hourly range
    for x in range(1, 5):
        curr_week = datetime.now() - timedelta(days=7 * x)
        for hour in range(7, 24):  # From 07:00 to 23:59
            range_start = curr_week.replace(hour=hour, minute=0, second=0, microsecond=0)
            range_end = curr_week.replace(hour=hour, minute=59, second=59, microsecond=0)

            for item in filtered_data:
                try:
                    time_in = datetime.strptime(item["Time_in"], "%Y-%m-%d %H:%M:%S")
                    time_out = datetime.strptime(item["Time_out"], "%Y-%m-%d %H:%M:%S")

                    # Check if entry is active in this time slot
                    if time_in <= range_end and time_out > range_start:
                        time_slots[f"{hour:02d}00-{hour:02d}59"] += 1
                except (KeyError, ValueError):
                    continue  # Skip invalid entries

    # Print results
    for hour in range(7, 24):  # From 07:00 to 23:59
        hour_range = f"{hour:02d}00-{hour:02d}59"
        print(f"{hour_range}: {time_slots[hour_range]}")

    return time_slots


def make_graph(time_slots_dict):
    times = ["0700", "0800", "0900", "1000", "1100", "1200", "1300", "1400", "1500", "1600", "1700", "1800", "1900", "2000", "2100", "2200", "2300"]

    capacity = list(time_slots_dict.values())

    average_capacity = sum(time_slots_dict.values()) / len(time_slots_dict)

    ticks_to_display = [0, 2, 4, 6, 8, 10, 12, 14, 16]
    labels_to_display = ["0700", "0900", "1100", "1300", "1500", "1700", "1900", "2100", "2300"]

    # Create a bar plot
    fig, ax = plt.subplots(figsize=(16, 8))
    bars = ax.bar(times, capacity, color="skyblue", width=0.9, align='center')

    # Styling the graph
    for bar in bars:
        bar.set_edgecolor('black')  # Optional: set a border color
        bar.set_linewidth(0.2)  # Optional: border width

    # Vertical Bar Plot
    ax.set_xlabel("Time", fontsize=14)
    ax.set_ylabel("Number of users")
    ax.set_title("Sunday Gym Usage", fontsize=18)
    ax.set_xticks(ticks_to_display, labels_to_display)

    ax.spines[["left", "top", "right"]].set_visible(False)
    ax.yaxis.set_visible(False)


    ax.bar_label(bars, padding=-15, color="black", label_type="edge", fontsize=12, fontweight="bold")

    ax.axhline(y=average_capacity, zorder=0, ls="-", lw=1.5, color="green", label="Average Capacity")
    ax.text(y=average_capacity, x=0, s=f"{round(average_capacity, 1)}", ha="center", bbox=dict(facecolor="white", edgecolor="green", ls = "-"))
    plt.legend(loc="upper left", fontsize=14)

    plt.tight_layout()
    plt.savefig('test.png', dpi=300)

    #plt.show()

#test_path = "test_data.json"

#input_dict = process_data(test_path)
#make_graph(input_dict)