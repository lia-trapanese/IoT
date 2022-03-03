from servo import servo
import pwm
import flash_memory
import mqtt_manager
import music

led = D22.PWM
buzzer = D18.PWM
pinMode(led, OUTPUT)
pinMode(buzzer, OUTPUT) 

#Starts the servos
def startServo(pwm_pin):
    initial_angle = 3
    s = servo.Servo(pwm_pin)
    s.attach()
    if(pwm_pin == D27.PWM):
        initial_angle = 70
    s.moveToDegree(initial_angle)
    return s

# Function executed by the LT (Lcd-Thread) to display time and messages to the needer
def lcd_loop(lcd, realClock, alarmEvent):
    print("\nLT - LCD initialized!\n")
    while True:
        lcd.clear()
        while alarmEvent.is_set():
            lcd.putstr("  Prelevare la      pillola!")
            sleep(1000)
            lcd.clear()
        now = realClock.get_time()
        lcd.putstr("    %02d:%02d:%02d"%now + "     " + day_of_week[now[6]] + " "+ "%02d/%02d/%d"%(now[3:6]) + " ")
        sleep(1000)

# Function executed by the led thread to blink when the alarm thread is set
def blink(pin, alarmEvent):
    while True:
        alarmEvent.wait()
        while alarmEvent.is_set():
            pwm.write(led, 13, int(13 * 0.94))
            sleep(300)
            pwm.write(led, 13, int(13 * 0.1))
            sleep(200)
        sleep(1000)

# Servo movements to drop the pill
def drop_pill(servos):
    #print("OPEN DOWN")
    servos[0].moveToDegree(30)
    sleep(100)
    #print("CLOSE DOWN")
    servos[0].moveToDegree(3)
    sleep(500)
    #print("OPEN UP")
    servos[1].moveToDegree(100)
    sleep(100)
    #print("CLOSE UP")
    servos[1].moveToDegree(70)

# Dictionary for the LCD display
day_of_week = {
    1: "Mon",
    2: "Tue",
    3: "Wed",
    4: "Thu",
    5: "Fri",
    6: "Sat",
    7: "Sun",
}

# Dictionary for the LCD display
month_formatter = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}