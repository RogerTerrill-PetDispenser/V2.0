import RPi.GPIO as GPIO
import threading
import time
import schedule
from datetime import datetime
from guizero import App, Text, PushButton, Window, Box

# Raspberry Pi 3 Pin Settings
LED = 11
DC_MOTOR = 13
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) # We are accessing GPIOs according to their physical location
GPIO.setup(LED, GPIO.OUT) # We have set our LED pin mode to output
GPIO.output(LED, GPIO.LOW) # When it will start then LED will be OFF

GPIO.setup(DC_MOTOR, GPIO.OUT) # We have set our LED pin mode to output
GPIO.output(DC_MOTOR, GPIO.LOW) # When it will start then LED will be OFF

# Raspberry Pi 3 Pin Settings
enabled = True
led_text = "OFF"
FOOD_DELAY = 6.80
MANUAL_FEED_PAUSE = 3600
current_time = ""

GREEN = "green"
RED = "red"
WHITE = "white"
BLUE = "#06BEE1"
# Function for Buttons started here


def manual_feed_toggle():
    if GPIO.input(LED):
        GPIO.output(LED, GPIO.LOW)
    else:
        GPIO.output(LED, GPIO.HIGH)
    print(GPIO.input(11))
    
    if GPIO.input(DC_MOTOR):
        GPIO.output(DC_MOTOR, GPIO.LOW)
    else:
        GPIO.output(DC_MOTOR, GPIO.HIGH)
    


def pause():
    global enabled
    enabled = not enabled
    pause_feed_button.text = "Binky Food Machine Is Paused" if not enabled else "Binky Food Machine Is Enabled"
    pause_feed_button.bg = RED if not enabled else GREEN
    if(not enabled):
        manual_single_feed_button.disable()
        manual_feed_toggle_button.disable()
    else:
        manual_single_feed_button.enable()
        manual_feed_toggle_button.enable()
    print("Enabled" if enabled else "Disabled")
    
    
def pause_after_manual_feed():
    global enabled
    enabled = False
    pause_feed_button.text = "Binky Food Machine Is Paused"
    pause_feed_button.bg = RED
    
    manual_single_feed_button.disable()
    manual_feed_toggle_button.disable()
    
    time.sleep(MANUAL_FEED_PAUSE)
    
    enabled = True
    pause_feed_button.text = "Binky Food Machine Is Enabled"
    pause_feed_button.bg = GREEN
    manual_single_feed_button.enable()
    manual_feed_toggle_button.enable()
    
    print("Enabled" if enabled else "Disabled")

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()
    
    
def single_feed():
    if enabled:
        feed_time = datetime.now()
        last_fed_time.value = current_time.strftime("%I:%M:%S %p")
        
        GPIO.output(LED, GPIO.HIGH)
        GPIO.output(DC_MOTOR, GPIO.HIGH)
        manual_single_feed_button.disable()
        manual_feed_toggle_button.disable()
        manual_feed_toggle_button.bg = WHITE
        manual_single_feed_button.bg = WHITE
        print("Manual Feeding the BINKY!!!")
        
        time.sleep(FOOD_DELAY)
        
        GPIO.output(LED, GPIO.LOW)
        GPIO.output(DC_MOTOR, GPIO.LOW)
        manual_single_feed_button.enable()
        manual_feed_toggle_button.enable()
        manual_feed_toggle_button.bg = BLUE
        manual_single_feed_button.bg = BLUE
        print("Done feeding")
    else:
        print("Sorry, binky machine is disabled")


def manual_single_feed():
    run_threaded(single_feed)
    run_threaded(pause_after_manual_feed)


def run_feeding_schedule():
    schedule.every().day.at("06:00").do(single_feed)
    schedule.every().day.at("18:00").do(single_feed)
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

# Title box
title_box_container = Box(app, width="fill", align="top", border=True)
title_box_left = Box(title_box_container, width="fill", align="left")
title_box_right = Box(title_box_container, width="fill", align="right")
header_text = Text(title_box_left, size=24, height="fill", width="fill")
last_fed_text = Text(title_box_right, size=24, align="top", height="fill", width="fill", text="Binky Last Fed")
last_fed_time = Text(title_box_right, size=24, align="bottom", height="fill", width="fill", text="--:--")

# Button box
buttons_box = Box(app, width="fill", height="fill", align="top", border=True)

manual_feed_toggle_button = PushButton(buttons_box, align="left", text="Toggle Feed", width="fill", height="fill", command=manual_feed_toggle)
manual_feed_toggle_button.bg = BLUE
manual_feed_toggle_button.text_color = WHITE
manual_feed_toggle_button.text_size = 16

manual_single_feed_button = PushButton(buttons_box, align="right", text="Manual Feed", width="fill", height="fill", command=manual_single_feed)
manual_single_feed_button.bg = BLUE
manual_single_feed_button.text_color = WHITE
manual_single_feed_button.text_size = 16

# Status box
status_box = Box(app, width="fill", height="fill", align="bottom", border=True)

pause_feed_button = PushButton(status_box, text="Binky Food Machine Is Enabled", width="fill", height="fill", command=pause)
pause_feed_button.bg = GREEN
pause_feed_button.text_color = WHITE
pause_feed_button.text_size = 16

run_threaded(run_feeding_schedule)
run_threaded(display_time)
app.display()


