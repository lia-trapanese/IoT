import rtc
import flash_memory
import mqtt_manager
import ds1307
import alarm_manager

# Used to convert week day number to corresponding JSON fields
realClockDayFormatter = {
    1: "monday",
    2: "tuesday",
    3: "wednesday",
    4: "thursday",
    5: "friday",
    6: "saturday",
    7: "sunday"
}

# Initialize the DS3231 real time clock, ready to read time from it
def init_realClock(i2c_port):
    realClock = ds1307.DS1307(i2c_port)
    realClock.start()
    return realClock

# Used to display to terminal the current time
def print_time(realClock):
     print("%02d:%02d:%02d - %02d/%02d/%d - %d"%realClock.get_time())

# Used to display to terminal the current timetable schedule
def print_time_table(userPillDictionary):
    print("TT - Time table:")
    for i in range(7):
        print("    ", realClockDayFormatter[i + 1],"-", userPillDictionary[realClockDayFormatter[i + 1] ])

# Function executed by the TT (Time-Thread), to check if it's pill time, and to set the alarm event
def realTimeCheckLoop(realClock, alarmEvent):
    effs = flash_memory.ExclusiveFlashFileStream.getInstance()
    userPillDictionary = flash_memory.readFlashJSON(effs)
    print_time_table(userPillDictionary)
    while(True):
        now = realClock.get_time()
        now_hour_min = [now[0], now[1]] # [Ora, Minuto]
        print("TT - Now and today schedule: ", str(now_hour_min[0]) + ":" + str(now_hour_min[1]) , "-", userPillDictionary[realClockDayFormatter[now[6]]])
        
        if now_hour_min in userPillDictionary[realClockDayFormatter[now[6]]]:
            print("TT - Ora della pillola!")
            alarmEvent.set()
        
        sleep(60000)
        userPillDictionary = flash_memory.readFlashJSON(effs)




# Clock ottenuto da internet, no DS3231
#while True:
#    sleep(12000)
#    print("MT - Ora modifico")
#    changes = [["monday",[[20, 58],[21, 0],[21, 2]]], ["wednesday", [[18, 5]]], ["pillName", "Cuore"]]
#    #changes = []
#    flash_memory.overrideFlashJSON(changes, exclusiveFlashFileStream)
#    sleep(120000)

#Segue: implementazione senza real time clock
#¶dayFormatter = {
#    0: "sunday",
#    1: "monday",
#    2: "tuesday",
#    3: "wednesday",
#    4: "thursday",
#    5: "friday",
#    6: "saturday"
#}
##def setRTC(timeStamp, timeZoneShift = 2):
#    rtc.set_utc(timeStamp + (timeZoneShift) * 60 * 60)
#def checkLoop(exclusiveFlashFileStream):
#    while(True):
#        userDictionary = flash_memory.readFlashJSON(exclusiveFlashFileStream)
#        time = rtc.get_utc()
#        t = [time.tm_hour, time.tm_min]
#        print(t)
#        print( userDictionary[ dayFormatter[time.tm_wday] ] )
#        if t in userDictionary[dayFormatter[time.tm_wday]]:
#            while True:
#                print("ALLARME")
#                sleep(6000)
#        #print(tm.tv_seconds)
#        #print(tm.tm_year,'/',tm.tm_month + 1,'/',tm.tm_mday,sep='')
#        print(time.tm_wday, ':', time.tm_hour,':',time.tm_min,':',time.tm_sec,sep='')
#        #print("pillola:", j["pillName"])
#        sleep(100000)