import wifi
import socketpool
import ssl
import adafruit_requests
import rtc
import time
import os

NETWORK1 = os.getenv("NETWORK1")
NETWORK1PASS = os.getenv("NETWORK1PASS")
NETWORK2 = os.getenv("NETWORK2")
NETWORK2PASS = os.getenv("NETWORK2PASS")
def connect_to_wifi():
    try:
        networks = wifi.radio.start_scanning_networks()
        time.sleep(1)
        for network in networks:
            if network.ssid == NETWORK1 or network.ssid == NETWORK2:
                SSID = network.ssid
                print(f"found netowork {network.ssid}")
                break
        if not SSID:
            raise ValueError("No Wifi Detected")
    except Exception as e:
        print(f"Failed to connect to WiFi: {e}")
    try:
        if SSID == NETWORK1:
            PASSWORD = NETWORK1PASS
        else:
            PASSWORD = NETWORK2PASS
        wifi.radio.connect(
    SSID,
    PASSWORD,  # This might be the user password or a specific network password
    )
        return True
    except Exception as e:
        print(f"Failed to connect to WiFi: {e}")
        return False

def set_time_from_ntp():
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())

    try:
        response = requests.get("http://worldtimeapi.org/api/ip")
        if response.status_code == 200:
            time_data = response.json()
            datetime_str = time_data['datetime']
            year, month, day = map(int, datetime_str[:10].split('-'))
            hour, minute, second = map(int, datetime_str[11:19].split(':'))
            rtc.RTC().datetime = time.struct_time((year, month, day, hour, minute, second, 0, -1, -1))
            print(f"Time set to {rtc.RTC().datetime}")
        else:
            print(f"Failed to get time, status code: {response.status_code}")
    except Exception as e:
        print(f"Exception occurred while setting time: {e}")
