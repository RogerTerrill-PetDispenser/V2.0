# ************************************************************************** #
# ****                                                                  **** #
# *********** Code Designed by www.TheEngineeringProjects.com ************** #
# ****                                                                  **** #
# ****************** How to Create a GUI in Raspberry Pi 3 ***************** #
# ****                                                                  **** #
# ************************************************************************** #

# Importing Libraries

import RPi.GPIO as GPIO
import threading
import time
import schedule
from datetime import date
from guizero import App, Text, PushButton, Window

# Raspberry Pi 3 Pin Settings

LED = 11 # pin11
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) # We are accessing GPIOs according to their physical location
GPIO.setup(LED, GPIO.OUT) # We have set our LED pin mode to output
GPIO.output(LED, GPIO.LOW) # When it will start then LED will be OFF

# Raspberry Pi 3 Pin Settings
enabled = True
led_text = "OFF"
# Funtion for Buttons started here

def manual_feed_toggle():
    if GPIO.input(11):
        GPIO.output(LED, GPIO.LOW)
    else:
        GPIO.output(LED, GPIO.HIGH)
    print(GPIO.input(11))

def pause():
    global enabled
    enabled = not enabled
    print("Disabled" if enabled else "Enabled")
    
def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()
    
    
def manual_single_feed():
    print("Manual Feeding the BINKY!!!")

def run_feeding_schedule():
    schedule.every().day.at("22:58").do(manual_single_feed)
    while True:
        schedule.run_pending()
        time.sleep(1)

app = App(title="Binky Food Machine V2")
manual_feed_toggle_button = PushButton(app, text="Toggle Feed", command=manual_feed_toggle, width="fill", height="fill")
manual_single_feed_button = PushButton(app, text="Manual Feed", command=manual_single_feed, width="fill", height="fill")
pause_feed_button = PushButton(app, text="Pause Binky Machine", command=pause, width="fill", height="fill")
run_threaded(run_feeding_schedule)
app.display()


