from display import display, clear_display
import alarm
import board

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
