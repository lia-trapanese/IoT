import streams
import json
import flash
import threading

STREAM_SIZE = 2048
STREAM_LOC = 0x00310000

# The filestream has to be sure of multiaccess from different threads,
# to do that is made synchronous and a singleton class, so there is only
# one instance of the filestream
class ExclusiveFlashFileStream:
    instance = 0
    def getInstance():
        if ExclusiveFlashFileStream.instance == None:
            print("Non esiste, lo creo")
            ExclusiveFlashFileStream()
        return ExclusiveFlashFileStream.instance
    def __init__(self, ffs):
        if ExclusiveFlashFileStream.instance != 0:
            print ("Questa classe e' un Singleton!")
        else:
            self.flashFileStream = ffs
            self.available = threading.Lock()
            ExclusiveFlashFileStream.instance = self
            return self
            
# Returns an exclusive filestream
def getExclusiveFlashStream():
    ff = flash.FlashFileStream(STREAM_LOC, STREAM_SIZE)
    return ExclusiveFlashFileStream(ff)

# Fields saved in flash memory
fields = ["name", "pin", "pillName", "count", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

def initFlash(name, pin, pillName, count):
    json = {
        "name":name,
        "pin":pin,
        "pillName":pillName,
        "count":count,
        "monday":[],
        "tuesday":[],
        "wednesday":[],
        "thursday":[],
        "friday":[],
        "saturday":[],
        "sunday":[]
    }
    return writeFlashJSON(json)

# To remove everything about a (or all) day in the flash memory
def clearDayFlashJSON(day):
    if day in fields[4:]:
        change = [day, []]
        overrideFlashJSON([change])
    elif day == "all":
        changes = [["monday", []], ["tuesday", []], ["wednesday", []], ["thursday", []], ["friday", []], ["saturday", []], ["sunday", []]]
        overrideFlashJSON(changes)
    else: 
        print(day, "non recognized!")

# To update pillcount, if a pill is dropped or if the user refills the stock
def change_pill_count(delta):
    effs = ExclusiveFlashFileStream.getInstance()
    json = readFlashJSON(effs)
    json["count"] = json["count"] + delta
    writeFlashJSON(json, effs)
    return json["count"]

# The function uset to update the flash memory, each change in changes is applied on the memory with only one total write
def overrideFlashJSON(changes):
    effs = ExclusiveFlashFileStream.getInstance()
    json = readFlashJSON(effs)
    for change in changes:
        if(change[0] in fields[2:]):
            json[change[0]] = change[1]
    writeFlashJSON(json, effs)

# This function acquire the lock and writes the new JSON on the flash memory
def writeFlashJSON(jsonToDump, effs = ExclusiveFlashFileStream.getInstance()):
    jsonToWrite = json.dumps(jsonToDump)
    effs.available.acquire()
    #print("LOCK BEFORE WRITE")
    effs.flashFileStream.write(len(jsonToWrite))
    effs.flashFileStream.write(jsonToWrite)
    effs.flashFileStream.flush()
    effs.flashFileStream.seek(0)
    effs.available.release()
    #print("UNLOCK AFTER WRITE)
    print("FF - Wrote", len(jsonToWrite), "bytes:", jsonToWrite)
    return effs

# This functions reads the current JSON stored in flash memory, used to check for the time check and to authenticate to exexute functions
def readFlashJSON(effs = ExclusiveFlashFileStream.getInstance()):
    effs.available.acquire()
    #print("LOCK BEFORE READ")
    numberOfBytes = effs.flashFileStream.read_int()
    stringJSON = effs.flashFileStream.read(numberOfBytes)
    effs.flashFileStream.seek(0)
    effs.available.release()
    #print("UNLOCK AFTER READ")
    #print("FF - Read", len(stringJSON), "bytes:", stringJSON)
    readJson = json.loads(stringJSON)
    return readJson

