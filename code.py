import board
import time
import digitalio
from calendar import fetch_events, filter_events, parse_datetime, parse_ical, sort_events
from network import connect_to_wifi, set_time_from_ntp
from version import version
from display import display_text, display_event, wrap_text, clear_display, display, CHARS_PER_LINE
from feathers3 import get_battery_voltage
import alarm

wifi = False

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
display_text([f"SchoolPad v.{version}", "Joshua Industries", "Connecting to WiFi...", "voltage: " + str(get_battery_voltage())])
if connect_to_wifi():
    wifi=True
    set_time_from_ntp()

    display_text([f"SchoolPad v.{version}", "Joshua Industries", "Fetching Events..."])
    fetched_ical = fetch_events()
    print("Events fetched")

    display_text([f"SchoolPad v.{version}", "Joshua Industries", "Parsing Events..."])
    parsed_ical = parse_ical(fetched_ical)
    sorted_ical = sort_events(parsed_ical)
    filtered_events = filter_events(sorted_ical)
    print("Events filtered")
else:
    display_text(["WiFi Connection Failed"])
    wifi=False
    time.sleep(0.5)
    display_text([f"SchoolPad v.{version}", "Joshua Industries", "Parsing Events..."])
    try:
        f = open("ical.txt", "r")
        fetched_ical = f.read()
        f.close()
    except:
        display_text(["Read Error. Reboot and contact support."])
        while True:
            continue
    parsed_ical = parse_ical(fetched_ical)
    sorted_ical = sort_events(parsed_ical)
    filtered_events = filter_events(sorted_ical)



# Initialize current position
current_pos = 0
total_events = len(filtered_events)
print(f"Total events: {total_events}")



# Display the first event initially
if total_events > 0:
    display_event(filtered_events[current_pos], current_pos)
else:
    display_text(wrap_text("No Events in next week", CHARS_PER_LINE))
    while True:
        pass
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
        if wifi:
            display_text([f"SchoolPad v.{version}", "Joshua Industries", "Fetching Events..."])
            try:
                fetched = fetch_events()  # Refresh events
            except:
                f = open("ical.txt", "r")
                fetched_ical = f.read()
                f.close()
                wifi=False

            print("Events fetched")
        else:
            if connect_to_wifi():
                display_text([f"SchoolPad v.{version}", "Joshua Industries", "Fetching Events..."])
                fetched = fetch_events()  # Refresh events
                print("Events fetched")
                wifi=True
            else:
                f = open("ical.txt", "r")
                fetched_ical = f.read()
                f.close()
                wifi=False
        display_text([f"SchoolPad v.{version}", "Joshua Industries", "Parsing Events..."])
        parsed_ical = parse_ical(fetched_ical)
        filtered_events = filter_events(parsed_ical)
        print("Events parsed")
        total_events = len(filtered_events)
        if total_events > 0:
            display_event(filtered_events[current_pos],current_pos)
        sleep= 0
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
    if sleep >= 3000:
        button_a.deinit()
        clear_display()
        display.sleep()
        alarm1 = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 60)
        pinalarm2 = alarm.pin.PinAlarm(pin=board.D9, value=False, pull=False)
        alarm.light_sleep_until_alarms(alarm1, pinalarm2)
        if alarm.wake_alarm == alarm1:
            button_a.deinit()
            pinalarm1 = alarm.pin.PinAlarm(pin=board.D9, value=False, pull=False)
            clear_display()
            display.sleep()
            sleep = 0
            alarm.exit_and_deep_sleep_until_alarms(pinalarm1)
        else:
            display.wake()
            button_a = digitalio.DigitalInOut(board.D9)  # Button A pin
            button_a.direction = digitalio.Direction.INPUT
            button_a.pull = digitalio.Pull.UP  # Use pull-up resistor
            current_pos = current_pos + 1
            sleep = 0
            refresh = 0


    if refresh >= 10:
        display_event(filtered_events[current_pos], current_pos)
        refresh = 0

    time.sleep(0.1)  # Short delay to avoid busy-waiting