import board
import digitalio
import storage
import time

dev_pin = digitalio.DigitalInOut(board.D14)  # Button A pin
dev_pin.direction = digitalio.Direction.INPUT
dev_pin.pull = digitalio.Pull.UP 

time.sleep(2)
if not dev_pin.value:  # Check if the pin is grounded
    storage.remount("/", readonly=True)
    print("dev")
else:
    storage.remount("/", readonly=False)
    print("production")