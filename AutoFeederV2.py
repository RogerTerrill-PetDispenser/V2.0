import RPi.GPIO as GPIO
import threading
import time
import schedule
from datetime import datetime
from guizero import App, Text, PushButton, Window

# Raspberry Pi 3 Pin Settings
LED = 11
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) # We are accessing GPIOs according to their physical location
GPIO.setup(LED, GPIO.OUT) # We have set our LED pin mode to output
GPIO.output(LED, GPIO.LOW) # When it will start then LED will be OFF

# Raspberry Pi 3 Pin Settings
enabled = True
led_text = "OFF"
food_delay = 8.100
current_time = ""
# Function for Buttons started here


def manual_feed_toggle():
    if GPIO.input(11):
        GPIO.output(LED, GPIO.LOW)
    else:
        GPIO.output(LED, GPIO.HIGH)
    print(GPIO.input(11))


def pause():
    global enabled
    enabled = not enabled
    pause_feed_button.text = "Binky Food Machine Is Paused" if not enabled else "Binky Food Machine Is Enabled"
    pause_feed_button.bg = "red" if not enabled else "green"
    if(not enabled):
        manual_single_feed_button.disable()
        manual_feed_toggle_button.disable()
    else:
        manual_single_feed_button.enable()
        manual_feed_toggle_button.enable()
    print("Enabled" if enabled else "Disabled")


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()
    
    
def single_feed():
    if enabled:
        GPIO.output(LED, GPIO.HIGH)
        manual_single_feed_button.disable()
        manual_feed_toggle_button.disable()
        manual_feed_toggle_button.bg = "white"
        manual_single_feed_button.bg = "white"
        print("Manual Feeding the BINKY!!!")
        
        time.sleep(food_delay)
        
        GPIO.output(LED, GPIO.LOW)
        manual_single_feed_button.enable()
        manual_feed_toggle_button.enable()
        manual_feed_toggle_button.bg = "green"
        manual_single_feed_button.bg = "green"
        print("Done feeding")
    else:
        print("Sorry, binky machine is disabled")


def manual_single_feed():
    run_threaded(single_feed)


def run_feeding_schedule():
    schedule.every().day.at("23:17").do(single_feed)
    while True:
        schedule.run_pending()
        time.sleep(1)
        
def display_time():
    global current_time
    while True:
        time.sleep(1)
        current_time = datetime.now()
        now = current_time.strftime("%I:%M:%S %p")
        date = current_time.strftime("%b %d, %Y")
        header_text.value = date + "\n" + now


app = App(title="Binky Food Machine V2")
header_text = Text(app, size=24)
manual_feed_toggle_button = PushButton(app, text="Toggle Feed", command=manual_feed_toggle, width="fill", height="fill")
manual_feed_toggle_button.bg = "green"
manual_feed_toggle_button.text_color = "white"
manual_feed_toggle_button.text_size = 16
manual_single_feed_button = PushButton(app, text="Manual Feed", command=manual_single_feed, width="fill", height="fill")
manual_single_feed_button.bg = "green"
manual_single_feed_button.text_color = "white"
manual_single_feed_button.text_size = 16
pause_feed_button = PushButton(app, text="Binky Food Machine Is Enabled", command=pause, width="fill", height="fill")
pause_feed_button.bg = "green"
pause_feed_button.text_color = "white"
pause_feed_button.text_size = 16
run_threaded(run_feeding_schedule)
run_threaded(display_time)
app.display()


