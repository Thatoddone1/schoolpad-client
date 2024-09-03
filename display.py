import displayio
import board
import adafruit_displayio_sh1107
import terminalio
from calendar import parse_datetime
from adafruit_display_text import label
import rtc
from adafruit_datetime import datetime
rtc_instance = rtc.RTC()

# Display setup


displayio.release_displays()
i2c = board.I2C()  # Uses board.SCL and board.SDA
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

WIDTH = 128
HEIGHT = 64
FONT_WIDTH = 6  # Approximate width of each character in pixels
FONT_HEIGHT = 8  # Approximate height of each character in pixels
LINE_SPACING = 2  # Space between lines
CHARS_PER_LINE = WIDTH // FONT_WIDTH

display = adafruit_displayio_sh1107.SH1107(
    display_bus, width=WIDTH, height=HEIGHT, rotation=0
)
display.wake()

#Display functions
def display_text(lines):
    splash = displayio.Group()
    for i, line in enumerate(lines):
        text_area = label.Label(terminalio.FONT, text=line, color=0xFFFFFF, x=0, y=(i * (FONT_HEIGHT + LINE_SPACING)) + 5)
        splash.append(text_area)
    display.root_group = splash

def clear_display():
    splash = displayio.Group()
    display.root_group = splash

def display_event(event, current_pos):
    wrapped_text = wrap_text(f"{current_pos}. " + event["SUMMARY"], CHARS_PER_LINE)
    parsed_start = parse_datetime(event["DTSTART"])
    parsed_end = parse_datetime(event["DTEND"])
    start = f"{parsed_start.hour:02d}:{parsed_start.minute:02d}"
    end = f"{parsed_end.hour:02d}:{parsed_end.minute:02d}"
    date = f"{parsed_start.month}/{parsed_start.day}"
    current_time = rtc_instance.datetime
    current_datetime = datetime(current_time.tm_year, current_time.tm_mon, current_time.tm_mday, 
                                current_time.tm_hour, current_time.tm_min, current_time.tm_sec)
    
    time_until=parsed_start - current_datetime
    total_seconds = int(time_until.total_seconds())
    minutes = total_seconds // 60
    if minutes < 0:
        time_until=parsed_end - current_datetime
        total_seconds = int(time_until.total_seconds())
        minutes = total_seconds // 60
    seconds = total_seconds % 60
    try:
        display_text([wrapped_text[0], wrapped_text[1], start, end, date, f"{minutes} min {seconds} seconds"])
    except:
        display_text([wrapped_text[0], start, end, date, f"{minutes} min {seconds} seconds"])


# Function to wrap text
def wrap_text(text, max_chars):
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 <= max_chars:
            if current_line:
                current_line += " "
            current_line += word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines
