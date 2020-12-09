import RPi.GPIO as GPIO
import os
import threading
import time
import schedule
from datetime import datetime
from guizero import App, Text, PushButton, Window, Box

# Raspberry Pi 3 Pin Settings
BUZZER_PIN = 21
DC_MOTOR_PIN = 13
PIR_PIN = 15
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) # We are accessing GPIOs according to their physical location

GPIO.setmode

GPIO.setup(PIR_PIN, GPIO.IN)

GPIO.setup(BUZZER_PIN, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

GPIO.setup(DC_MOTOR_PIN, GPIO.OUT) # We have set our LED pin mode to output
GPIO.output(DC_MOTOR_PIN, GPIO.LOW) # When it will start then LED will be OFF

# Raspberry Pi 3 Pin Settings
enabled = True
led_text = "OFF"
FOOD_DELAY = 6.80
MANUAL_FEED_PAUSE = 3600
BUTTON_TEXT_SIZE = 60
DISPLAY_ON_TIME = 5 #wait time in seconds
current_time = ""
display_on = True
time_since_motion_detected = time.time()

GREEN = "green"
RED = "red"
WHITE = "white"
BLUE = "#06BEE1"
# Function for Buttons started here


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
    
    
def SetDisplay(DisplayOn):
    cmd="" 
    if DisplayOn==True:
        cmd="sudo xset dpms force on"
    else:
        cmd="sudo xset dpms force off"
    if cmd is not "":
        print("Display-Status: "+str(DisplayOn))
        print(cmd)
        os.system(cmd)
        #wait 10 seconds, cause of the detection time of the PIR_PIN
        time.sleep(1)
        

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()
    
    
def single_feed():
    play(final_countdown_melody, final_countdown_tempo, 0.30, 1.2000)
    if enabled:
        feed_time = datetime.now()
        last_fed_time.value = current_time.strftime("%I:%M:%S %p")
        
        GPIO.output(LED, GPIO.HIGH)
        GPIO.output(DC_MOTOR_PIN, GPIO.HIGH)
        manual_single_feed_button.disable()
        manual_feed_toggle_button.disable()
        manual_feed_toggle_button.bg = WHITE
        manual_single_feed_button.bg = WHITE
        print("Manual Feeding the BINKY!!!")
        
        time.sleep(FOOD_DELAY)
        
        GPIO.output(LED, GPIO.LOW)
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
    global time_since_motion_detected
    DisplayOn=True
    i=0
    while True:
        time.sleep(0.1)
        i=i+1
        if i==10:
            i=0
            if DisplayOn==True:
                print("Time-Out: "+str(DISPLAY_ON_TIME-round(time.time()- time_since_motion_detected)))
        if GPIO.input(PIR_PIN)==1:
            time_since_motion_detected = time.time()
            if DisplayOn==False:
                DisplayOn=True
                SetDisplay(True)
        if DisplayOn==True:
            if time.time()- time_since_motion_detected > DISPLAY_ON_TIME:
                #time is over, screen off
                DisplayOn=False
                SetDisplay(False)

notes = {
	'B0' : 31,
	'C1' : 33, 'CS1' : 35,
	'D1' : 37, 'DS1' : 39,
	'EB1' : 39,
	'E1' : 41,
	'F1' : 44, 'FS1' : 46,
	'G1' : 49, 'GS1' : 52,
	'A1' : 55, 'AS1' : 58,
	'BB1' : 58,
	'B1' : 62,
	'C2' : 65, 'CS2' : 69,
	'D2' : 73, 'DS2' : 78,
	'EB2' : 78,
	'E2' : 82,
	'F2' : 87, 'FS2' : 93,
	'G2' : 98, 'GS2' : 104,
	'A2' : 110, 'AS2' : 117,
	'BB2' : 123,
	'B2' : 123,
	'C3' : 131, 'CS3' : 139,
	'D3' : 147, 'DS3' : 156,
	'EB3' : 156,
	'E3' : 165,
	'F3' : 175, 'FS3' : 185,
	'G3' : 196, 'GS3' : 208,
	'A3' : 220, 'AS3' : 233,
	'BB3' : 233,
	'B3' : 247,
	'C4' : 262, 'CS4' : 277,
	'D4' : 294, 'DS4' : 311,
	'EB4' : 311,
	'E4' : 330,
	'F4' : 349, 'FS4' : 370,
	'G4' : 392, 'GS4' : 415,
	'A4' : 440, 'AS4' : 466,
	'BB4' : 466,
	'B4' : 494,
	'C5' : 523, 'CS5' : 554,
	'D5' : 587, 'DS5' : 622,
	'EB5' : 622,
	'E5' : 659,
	'F5' : 698, 'FS5' : 740,
	'G5' : 784, 'GS5' : 831,
	'A5' : 880, 'AS5' : 932,
	'BB5' : 932,
	'B5' : 988,
	'C6' : 1047, 'CS6' : 1109,
	'D6' : 1175, 'DS6' : 1245,
	'EB6' : 1245,
	'E6' : 1319,
	'F6' : 1397, 'FS6' : 1480,
	'G6' : 1568, 'GS6' : 1661,
	'A6' : 1760, 'AS6' : 1865,
	'BB6' : 1865,
	'B6' : 1976,
	'C7' : 2093, 'CS7' : 2217,
	'D7' : 2349, 'DS7' : 2489,
	'EB7' : 2489,
	'E7' : 2637,
	'F7' : 2794, 'FS7' : 2960,
	'G7' : 3136, 'GS7' : 3322,
	'A7' : 3520, 'AS7' : 3729,
	'BB7' : 3729,
	'B7' : 3951,
	'C8' : 4186, 'CS8' : 4435,
	'D8' : 4699, 'DS8' : 4978
}
                
final_countdown_melody = [
	notes['A3'],notes['E5'],notes['D5'],notes['E5'],notes['A4'],
	notes['F3'],notes['F5'],notes['E5'],notes['F5'],notes['E5'],notes['D5'],
	notes['D3'],notes['F5'],notes['E5'],notes['F5'],notes['A4'],
	notes['G3'],0,notes['D5'],notes['C5'],notes['D5'],notes['C5'],notes['B4'],notes['D5'],
	notes['C5'],notes['A3'],notes['E5'],notes['D5'],notes['E5'],notes['A4'],
	notes['F3'],notes['F5'],notes['E5'],notes['F5'],notes['E5'],notes['D5'],
	notes['D3'],notes['F5'],notes['E5'],notes['F5'],notes['A4'],
	notes['G3'],0,notes['D5'],notes['C5'],notes['D5'],notes['C5'],notes['B4'],notes['D5'],
	notes['C5'],notes['B4'],notes['C5'],notes['D5'],notes['C5'],notes['D5'],
	notes['E5'],notes['D5'],notes['C5'],notes['B4'],notes['A4'],notes['F5'],
	notes['E5'],notes['E5'],notes['F5'],notes['E5'],notes['D5'],
	notes['E5'],
]

final_countdown_tempo = [
	1,16,16,4,4,
	1,16,16,8,8,4,
	1,16,16,4,4,
	2,4,16,16,8,8,8,8,
	4,4,16,16,4,4,
	1,16,16,8,8,4,
	1,16,16,4,4,
	2,4,16,16,8,8,8,8,
	4,16,16,4,16,16,
	8,8,8,8,4,4,
	2,8,4,16,16,
	1,
]



def play(melody,tempo,pause,pace=0.800):
    for i in range(0, len(melody)):		# Play song
        noteDuration = pace/tempo[i]
        buzz(melody[i],noteDuration)	# Change the frequency along the song note
        
        pauseBetweenNotes = noteDuration * pause
        time.sleep(pauseBetweenNotes)

def buzz(frequency, length):	 #create the function "buzz" and feed it the pitch and duration)
    if(frequency==0):
        time.sleep(length)
        return
    period = 1.0 / frequency 		 #in physics, the period (sec/cyc) is the inverse of the frequency (cyc/sec)
    delayValue = period / 2		 #calcuate the time for half of the wave
    numCycles = int(length * frequency)	 #the number of waves to produce is the duration times the frequency
    
    for i in range(numCycles):		#start a loop from 0 to the variable "cycles" calculated above
        GPIO.output(BUZZER_PIN, True)	 #set pin 27 to high
        time.sleep(delayValue)		#wait with pin 27 high
        GPIO.output(BUZZER_PIN, False)		#set pin 27 to low
        time.sleep(delayValue)		#wait with pin 27 low
        

    


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
manual_feed_toggle_button.text_size = BUTTON_TEXT_SIZE

manual_single_feed_button = PushButton(buttons_box, align="right", text="Manual Feed", width="fill", height="fill", command=manual_single_feed)
manual_single_feed_button.bg = BLUE
manual_single_feed_button.text_color = WHITE
manual_single_feed_button.text_size = BUTTON_TEXT_SIZE

# Status box
status_box = Box(app, width="fill", height="fill", align="bottom", border=True)

pause_feed_button = PushButton(status_box, text="Binky Food Machine Is Enabled", width="fill", height="fill", command=pause)
pause_feed_button.bg = GREEN
pause_feed_button.text_color = WHITE
pause_feed_button.text_size = BUTTON_TEXT_SIZE

run_threaded(run_feeding_schedule)
run_threaded(display_time)
run_threaded(motion_detection)
app.display()


