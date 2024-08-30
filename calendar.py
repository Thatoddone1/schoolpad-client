import wifi
import socketpool
import ssl
import adafruit_requests
from adafruit_datetime import datetime, timedelta
import rtc
import os

# Create a socket pool and SSL context
pool = socketpool.SocketPool(wifi.radio)
ssl_context = ssl.create_default_context()
requests = adafruit_requests.Session(pool, ssl_context=ssl_context)

# Define your API URL
api_url = os.getenv("WEBCAL")

def fetch_events():
    print("Fetching events...")
    try:
        response = requests.get(api_url)
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            try:
                f = open("ical.txt", "w")
                f.write(response.text)
                f.close()
            except:
                print("file error")
        else:
            print(f"Error fetching events, status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"Exception occurred while fetching events: {e}")
        return []
    return response.text


def parse_ical(ical_data):
    events = []
    current_event = None
    for line in ical_data.split('\n'):
        line = line.strip()
        
        if line == 'BEGIN:VEVENT':
            current_event = {}
        elif line == 'END:VEVENT':
            if current_event:
                events.append(current_event)
                current_event = None
        elif current_event is not None:
            if ':' in line:
                key, value = line.split(':', 1)
                if ';' in key:
                    key = key.split(';')[0]
                current_event[key] = value
    
    return events


def sort_events(events):
    """
    Sort events by their start date and time.
    Assumes that the events have a 'DTSTART' key with date-time in the format 'YYYYMMDDTHHMMSS'.
    """
    def event_start_key(event):
        dtstart = event.get('DTSTART', '')
        # If DTSTART is a list, get the first element
        if isinstance(dtstart, list):
            dtstart = dtstart[0]
        return dtstart
    
    return sorted(events, key=event_start_key)



def parse_datetime(datetime_str):
    """Parse a datetime string in the format YYYYMMDDTHHMMSS or YYYYMMDD."""
    try:
        if 'T' in datetime_str:
            year = int(datetime_str[:4])
            month = int(datetime_str[4:6])
            day = int(datetime_str[6:8])
            hour = int(datetime_str[9:11])
            minute = int(datetime_str[11:13])
            second = int(datetime_str[13:15])
            return datetime(year, month, day, hour, minute, second)
        else:
            year = int(datetime_str[:4])
            month = int(datetime_str[4:6])
            day = int(datetime_str[6:8])
            return datetime(year, month, day)
    except ValueError as e:
        print(f"Error parsing datetime: {datetime_str}, Error: {e}")
        return None

def filter_events(parsed_events):
    filtered_events = []
    rtc_instance = rtc.RTC()
    current_time = rtc_instance.datetime
    current_datetime = datetime(current_time.tm_year, current_time.tm_mon, current_time.tm_mday, 
                                0, 0, 0)
    one_week_future = current_datetime + timedelta(days=7)

    print(f"Current datetime: {current_datetime}")
    print(f"One week future: {one_week_future}")

    for event in parsed_events:
        start_date_str = event.get('DTSTART', '')
        if start_date_str.startswith('VALUE=DATE:'):
            start_date_str = start_date_str.split(':')[1]
        
        try:
            start_date = parse_datetime(start_date_str)
            if start_date is None:
                continue
          #  print(f"Event: {event.get('SUMMARY', 'Unknown Event')}, Start date: {start_date}")
            
            if current_datetime <= start_date <= one_week_future:
                filtered_events.append(event)
        except ValueError:
            print(f"Couldn't parse date for event: {event.get('SUMMARY', 'Unknown Event')}")

    print(f"Filtered {len(filtered_events)} events within the next week")
    return filtered_events
