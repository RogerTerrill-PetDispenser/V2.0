import RPi.GPIO as GPIO
import os
import threading
import time
import schedule
import music
from datetime import datetime
from guizero import App, Text, PushButton, Box

# Raspberry Pi Pin Assignments
DC_MOTOR_PIN = 13
PIR_PIN = 15
BUZZER_PIN = 21

# GPIO Setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)  # We are accessing GPIOs according to their physical location
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(DC_MOTOR_PIN, GPIO.OUT)
GPIO.output(DC_MOTOR_PIN, GPIO.LOW)

# Constants, Times in Seconds
FOOD_DELAY = 6.80
MANUAL_FEED_PAUSE = 3600
DISPLAY_ON_TIME = 60
BUTTON_TEXT_SIZE = 60

# Color Constants
GREEN = "green"
RED = "red"
WHITE = "white"
BLUE = "#06BEE1"

# Global Variables
enabled = True
current_time = ""
display_on = True
time_since_motion_detected = time.time()


def manual_feed_toggle():
    if GPIO.input(DC_MOTOR_PIN):
        GPIO.output(DC_MOTOR_PIN, GPIO.LOW)
    else:
        GPIO.output(DC_MOTOR_PIN, GPIO.HIGH)


def pause():
    global enabled
    enabled = not enabled
    pause_feed_button.text = "Binky Food Machine Is Paused" if not enabled else "Binky Food Machine Is Enabled"
    pause_feed_button.bg = RED if not enabled else GREEN
    if not enabled:
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


def set_display(display_status):
    if display_status:
        cmd = "sudo xset dpms force on"
    else:
        cmd = "sudo xset dpms force off"
    if cmd is not "":
        print("Display-Status: " + str(display_status))
        print(cmd)
        os.system(cmd)
        time.sleep(1)  # Checks every second for motion


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def single_feed():
    play(music.crazy_frog_melody, music.crazy_frog_tempo,0.30,0.900)
    if enabled:
        last_fed_time.value = current_time.strftime("%I:%M:%S %p")

        GPIO.output(DC_MOTOR_PIN, GPIO.HIGH)
        manual_single_feed_button.disable()
        manual_feed_toggle_button.disable()
        manual_feed_toggle_button.bg = WHITE
        manual_single_feed_button.bg = WHITE
        print("Manual Feeding the BINKY!!!")

        time.sleep(FOOD_DELAY)

        GPIO.output(DC_MOTOR_PIN, GPIO.LOW)
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


def motion_detection():
    global time_since_motion_detected, display_on
    display_on = True
    i = 0
    while True:
        time.sleep(0.1)
        if GPIO.input(PIR_PIN) == 1:
            time_since_motion_detected = time.time()
            if not display_on:
                display_on = True
                set_display(True)
        if display_on:
            if time.time() - time_since_motion_detected > DISPLAY_ON_TIME:
                # time is over, screen off
                display_on = False
                set_display(False)


def play(melody, tempo, pause_tempo, pace=0.800):
    for i in range(0, len(melody)):  # Play song
        note_duration = pace / tempo[i]
        buzz(melody[i], note_duration)  # Change the frequency along the song note

        pause_between_notes = note_duration * pause_tempo
        time.sleep(pause_between_notes)


def buzz(frequency, length):  # create the function "buzz" and feed it the pitch and duration)
    if frequency == 0:
        time.sleep(length)
        return
    period = 1.0 / frequency  # in physics, the period (sec/cyc) is the inverse of the frequency (cyc/sec)
    delay_value = period / 2  # calculate the time for half of the wave
    num_cycles = int(length * frequency)  # the number of waves to produce is the duration times the frequency

    for i in range(num_cycles):  # start a loop from 0 to the variable "cycles" calculated above
        GPIO.output(BUZZER_PIN, True)  # set pin 27 to high
        time.sleep(delay_value)  # wait with pin 27 high
        GPIO.output(BUZZER_PIN, False)  # set pin 27 to low
        time.sleep(delay_value)  # wait with pin 27 low


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
manual_feed_toggle_button = PushButton(buttons_box, align="left", text="Toggle Feed", width="fill", height="fill",
                                       command=manual_feed_toggle)
manual_feed_toggle_button.bg = BLUE
manual_feed_toggle_button.text_color = WHITE
manual_feed_toggle_button.text_size = BUTTON_TEXT_SIZE
manual_single_feed_button = PushButton(buttons_box, align="right", text="Manual Feed", width="fill", height="fill",
                                       command=manual_single_feed)
manual_single_feed_button.bg = BLUE
manual_single_feed_button.text_color = WHITE
manual_single_feed_button.text_size = BUTTON_TEXT_SIZE

# Status box
status_box = Box(app, width="fill", height="fill", align="bottom", border=True)

pause_feed_button = PushButton(status_box, text="Binky Food Machine Is Enabled", width="fill", height="fill",
                               command=pause)
pause_feed_button.bg = GREEN
pause_feed_button.text_color = WHITE
pause_feed_button.text_size = BUTTON_TEXT_SIZE

run_threaded(run_feeding_schedule)
run_threaded(display_time)
run_threaded(motion_detection)
app.display()
