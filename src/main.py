import i2c_lcd
import streams
import threading
import flash_memory
import music
import mqtt_manager
import alarm_manager
import time_manager
        
sleep(2500)
streams.serial()
sleep(1000)
pinMode(D5, INPUT_PULLUP)

#Initialize the flash memory (the singleton thread-safe class)
flash_memory.getExclusiveFlashStream() 
realClock = time_manager.init_realClock(I2C1)
# To set up clock use 
#realClock.set_time(12, 48, 50, 27, 5, 2020, 3) 

#Event
alarmEvent = threading.Event()
#Servos
pinMode(D21.PWM, OUTPUT)
pinMode(D27.PWM, OUTPUT)
servos = [alarm_manager.startServo(D21.PWM), alarm_manager.startServo(D27.PWM)]

sleep(150)

# Launch the Mqtt-Thread   (MT): Set up the client to publish on PillNotifyR and to listen JSON functions called by the user
mqtt_manager.MqttConnection()

# Launch the Time-Thread   (TT): Checks if it's pill assumption time using the timetable stored in flash memory.
# If it's the right time, activates the threading.Event alarmEvent
thread(time_manager.realTimeCheckLoop, realClock, alarmEvent) 

# Launch the  LCD-Thread   (LT): Sets up LCD and displays time and messages for the needer
thread(alarm_manager.lcd_loop, i2c_lcd.I2CLcd(I2C0), realClock, alarmEvent) 

# Launch the LED and Music-Threads: When the alarmEvent is set up, the alarm tune is played and the LED blinks
thread(music.reproduce, music.notes, music.durations, alarm_manager.buzzer, alarmEvent)
thread(alarm_manager.blink, alarm_manager.led, alarmEvent)

# The main functions as the Alarm-Thread (AT): If the alarm event is activated, he plays the alarm after the pill drops
while True:
    print("AT - Waiting for pill event")
    alarmEvent.wait()
    print("AT - It's pill time!")
    alarm_manager.drop_pill(servos)
    sleep(1000)
    remaining_pills = flash_memory.change_pill_count(-1)
    if(remaining_pills <= 3):
        mqtt_manager.MqttConnection.publishMessage("There are only " + str(remaining_pills) + " pills left!")
    j = 0
    while True:
        if(digitalRead(D5)):
            print("AT - Pill was taken!")
            mqtt_manager.MqttConnection.publishMessage("Pill was taken after " + "%.2F" % (j/5) + " seconds!")
            sleep(100)
            alarmEvent.clear()
            break
        sleep(200)
        j = j + 1
