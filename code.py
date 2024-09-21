import board
import time
import digitalio
from calendar import fetch_events, filter_events, parse_datetime, parse_ical, sort_events
from network import connect_to_wifi, set_time_from_ntp
from version import version
from display import display_text, display_event, wrap_text, clear_display, display, CHARS_PER_LINE
from feathers3 import get_battery_voltage
import alarm
import neopixel
import json
import rtc

wifi = False

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel.fill([0,255,0])

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
rtc_instance = rtc.RTC
#if rtc_instance.datetime.tm_year == 2000:
display_text([f"SchoolPad v.{version}", "Joshua Industries", "Connecting to Wifi", "Setting time NTP", "voltage: " + str(get_battery_voltage())])
if connect_to_wifi():
    set_time_from_ntp()
    wifi=True
    print("wifi success")
#    else:
#        display_text(["Time protocol faliure", "Get near programmed wifi", "and click Reset Button"])

# Wi-Fi and Event Processing
display_text([f"SchoolPad v.{version}", "Joshua Industries", "Quick Boot Started", "voltage: " + str(get_battery_voltage())])
try:
    f = open("filtered_ical.json", "r")
    filtered_events = json.loads(f.read())
    wifi = False
except:
    try:
        f = open("ical.txt", "r")
        fetched_ical = f.read()
        f.close()
    except:
        fetched_ical = fetch_events()
        f = open("ical.txt", "w")
        f.write(fetched_ical)
        f.close()
    display_text([f"SchoolPad v.{version}", "Joshua Industries", "Quick Boot Fail", "Parsing Events..."])
    parsed_ical = parse_ical(fetched_ical)
    sorted_ical = sort_events(parsed_ical)
    filtered_events = filter_events(sorted_ical)
    f = open("filtered_ical.json", "w")
    f.write(json.dumps(filtered_events))
    f.close()
    wifi=False


# Initialize current position
current_pos = 0
total_events = len(filtered_events)
print(f"Total events: {total_events}")



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
            display_text([f"SchoolPad v.{version}", "Joshua Industries", "Refreshing Event Lists..."])
            try:
                fetched_ical = fetch_events()
                f = open("ical.txt", "w")
                f.write(fetched_ical)
                f.close()
                parsed_ical = parse_ical(fetched_ical)
                sorted_ical = sort_events(parsed_ical)
                filtered_events = filter_events(sorted_ical)  # Refresh events
                f = open("filtered_ical.json", "w")
                f.write(json.dumps(filtered_events))
                f.close()
                set_time_from_ntp()
            except:
                try:
                    f = open("filtered_ical.json", "r")
                    filtered_events = json.loads(f.read())
                    f.close()
                    wifi = False
                except:
                    f = open("ical.txt", "r")
                    fetched_ical = f.read()
                    f.close()
                    display_text([f"SchoolPad v.{version}", "Joshua Industries", "Parsing Events..."])
                    parsed_ical = parse_ical(fetched_ical)
                    sorted_ical = sort_events(parsed_ical)
                    filtered_events = filter_events(sorted_ical)
                    wifi=False

            print("Events fetched")
        else:
            if connect_to_wifi():
                display_text([f"SchoolPad v.{version}", "Joshua Industries", "Refreshing Event Lists..."])
                fetched_ical = fetch_events()  # Refresh events
                print("Events fetched")
                f = open("ical.txt", "w")
                f.write(fetched_ical)
                f.close()
                parsed_ical = parse_ical(fetched_ical)
                sorted_ical = sort_events(parsed_ical)
                filtered_events = filter_events(sorted_ical)  # Refresh events
                f = open("filtered_ical.json", "w")
                f.write(json.dumps(filtered_events))
                f.close()
                wifi=True
                set_time_from_ntp()
            else:
                try:
                    f = open("filtered_ical.json", "r")
                    filtered_events = json.loads(f.read())
                    f.close()
                    wifi=False
                except:
                    f = open("ical.txt", "r")
                    fetched_ical = f.read()
                    display_text([f"SchoolPad v.{version}", "Joshua Industries", "Parsing Events..."])
                    parsed_ical = parse_ical(fetched_ical)
                    sorted_ical = sort_events(parsed_ical)
                    filtered_events = filter_events(sorted_ical)
                    print("Events parsed")
                    f.close()
                    wifi=False
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
