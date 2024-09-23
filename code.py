import board
import time
import digitalio
from calendar import fetch_events, filter_events, parse_datetime, parse_ical, sort_events
from network import connect_to_wifi, set_time_from_ntp, is_wifi_connected, refresh_wifi_if_needed
from version import version
from display import display_text, display_event, wrap_text, clear_display, display, CHARS_PER_LINE
from feathers3 import get_battery_voltage
import alarm
import json
import rtc
print(rtc.RTC().datetime)
if rtc.RTC().datetime.tm_year==2000:
    display_text([f"SchoolPad v.{version}", "Joshua Industries", "Wifi Connecting", "voltage: " + str(get_battery_voltage())])
    if connect_to_wifi():
        set_time_from_ntp()

SLEEP_TIMEOUT = 30

# Button setup
button_a = digitalio.DigitalInOut(board.D9)  # Button A pin
button_a.direction = digitalio.Direction.INPUT
button_a.pull = digitalio.Pull.UP  # Use pull-up resistor

button_c = digitalio.DigitalInOut(board.D5)  # Button C pin
button_c.direction = digitalio.Direction.INPUT
button_c.pull = digitalio.Pull.UP  # Use pull-up resistor

button_b = digitalio.DigitalInOut(board.D6)  # Button B pin (for refreshing events)
button_b.direction = digitalio.Direction.INPUT
button_b.pull = digitalio.Pull.UP  # Use pull-up resistor



# Wi-Fi and Event Processing
display_text([f"SchoolPad v.{version}", "Joshua Industries", "Quick Boot Started", "voltage: " + str(get_battery_voltage())])
try:
    f = open("filtered_ical.json", "r")
    filtered_events = json.loads(f.read())
except:
    display_text([f"SchoolPad v.{version}", "Joshua Industries", "Quick Boot Fail", "Parsing Events..."])
    try:
        f = open("ical.txt", "r")
        fetched_ical = f.read()
        f.close()
    except:
        fetched_ical = fetch_events()
        f = open("ical.txt", "w")
        f.write(fetched_ical)
        f.close()
    parsed_ical = parse_ical(fetched_ical)
    sorted_ical = sort_events(parsed_ical)
    filtered_events = filter_events(sorted_ical)
    f = open("filtered_ical.json", "w")
    f.write(json.dumps(filtered_events))
    f.close()


# Initialize current position
if alarm.sleep_memory[1]:
    current_pos = alarm.sleep_memory[0]
else:
    current_pos = 0
total_events = len(filtered_events)


def enter_deep_sleep_mode(current_pos):
    clear_display()
    display.sleep()
    alarm.sleep_memory[1] = True
    alarm.sleep_memory[0] = current_pos
    pinalarm1 = alarm.pin.PinAlarm(pin=board.D9, value=False, pull=False)
    alarm.exit_and_deep_sleep_until_alarms(pinalarm1)
def enter_light_sleep_mode():
    clear_display()
    display.sleep()
    alarm1 = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 60)
    pinalarm2 = alarm.pin.PinAlarm(pin=board.D9, value=False, pull=False)
    alarm.light_sleep_until_alarms(alarm1, pinalarm2)
    if alarm.wake_alarm == alarm1:
        return True
    else:
        return False
def button_deinit():
    button_a.deinit()
    button_b.deinit()
    button_c.deinit()

def button_reinit():
    global button_a, button_b, button_c
    button_a = digitalio.DigitalInOut(board.D9)  # Button A pin
    button_a.direction = digitalio.Direction.INPUT
    button_a.pull = digitalio.Pull.UP  # Use pull-up resistor

    button_c = digitalio.DigitalInOut(board.D5)  # Button C pin
    button_c.direction = digitalio.Direction.INPUT
    button_c.pull = digitalio.Pull.UP  # Use pull-up resistor

    button_b = digitalio.DigitalInOut(board.D6)  # Button B pin (for refreshing events)
    button_b.direction = digitalio.Direction.INPUT
    button_b.pull = digitalio.Pull.UP  # Use pull-up resistor

def refresh_events():
    try:
        if refresh_wifi_if_needed():
            fetched_ical = fetch_events()
            with open("ical.txt", "w") as f:
                f.write(fetched_ical)
                f.close()
            set_time_from_ntp()
        else:
            with open("ical.txt", "r") as f:
                fetched_ical = f.read()
                f.close()

        parsed_ical = parse_ical(fetched_ical)
        sorted_ical = sort_events(parsed_ical)
        filtered_events = filter_events(sorted_ical)
        with open("filtered_ical.json", "w") as f:
            json.dump(filtered_events, f)
        print("Events fetched and processed")
    except Exception as e:
        print(f"Error refreshing events: {e}")
        try:
            with open("filtered_ical.json", "r") as f:
                filtered_events = json.load(f)
        except:
            display_text([f"SchoolPad v.{version}", "Joshua Industries", "Error: Unable to refresh or load events"])
            filtered_events = []

    return filtered_events



# Display the first event initially
if total_events > 0:
    display_event(filtered_events[current_pos], current_pos)
else:
    display_text(wrap_text("No Events in next week", CHARS_PER_LINE))
    time.sleep(1)
    button_a.deinit()
    pinalarm1 = alarm.pin.PinAlarm(pin=board.D9, value=False, pull=False)
    clear_display()
    display.sleep()
    alarm.exit_and_deep_sleep_until_alarms(pinalarm1)

# Track button states
last_button_a_state = button_a.value
last_button_c_state = button_c.value
last_button_b_state = button_b.value

sleep = 0
refresh = 0
# Main loop
while True:
    current_button_a_state = button_a.value
    current_button_c_state = button_c.value
    current_button_b_state = button_b.value

    if not current_button_a_state and last_button_a_state:  # Button A is pressed
        current_pos = (current_pos - 1) % total_events  # Move to the previous event
        display_event(filtered_events[current_pos], current_pos)
        sleep=0
        refresh=0
        time.sleep(0.2)  # Debounce delay

    if not current_button_c_state and last_button_c_state:  # Button C is pressed
        current_pos = (current_pos + 1) % total_events  # Move to the next event
        display_event(filtered_events[current_pos], current_pos)
        sleep=0
        refresh=0
        time.sleep(0.2)  # Debounce delay
    if not current_button_b_state and last_button_b_state:  # Button B is pressed
        display_text([f"SchoolPad v.{version}", "Joshua Industries", "Refreshing Event Lists..."])
        filtered_events = refresh_events()
        total_events = len(filtered_events)
        if total_events > 0:
            display_event(filtered_events[current_pos], current_pos)
        sleep = 0
        refresh = 0
        time.sleep(0.2)  # Debounce delay
# state checking
    last_button_a_state = current_button_a_state
    last_button_c_state = current_button_c_state
    last_button_b_state = current_button_b_state


#timers
    sleep = sleep + 1
    refresh = refresh + 1

#timer checks
    if sleep >= SLEEP_TIMEOUT:
        button_deinit()
        if enter_light_sleep_mode():
            enter_deep_sleep_mode(current_pos)
        else:
            button_reinit()
            display.wake()
            sleep = 0
            refresh = 0


    if refresh >= 10:
        display_event(filtered_events[current_pos], current_pos)
        refresh = 0

    time.sleep(0.1)  # Short delay to avoid busy-waiting
