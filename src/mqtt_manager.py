from mqtt import mqtt
from wireless import wifi
from espressif.esp32net import esp32wifi as wifi_driver
import flash_memory
import json
wifi_driver.auto_init()

AP_NAME = "Rete Triuzzi"

AP_PASSWORD = "abcdefg1997"

#SERVER = "test.mosquitto.org"
#SERVER = "broker.hivemq.com"
SERVER = "broker.mqttdashboard.com"

CLIENT_NAME = "SAL-039"
NEEDER_TOPIC = "PillNotify/Needer" # Where you receive commands
RELATIVE_TOPIC = "PillNotify/Relative" # You send there the comunications

PUBLISH = mqtt.PUBLISH

class MqttConnection:
    client = 0
    def init():
        print("MT - Tentativo di connessione alla rete", AP_NAME)#, "con password", AP_PASSWORD)
        for retry in range(20):
            try:
                wifi.link(AP_NAME, wifi.WIFI_WPA2, AP_PASSWORD)
                break
            except Exception as e:
                k = 0
                #print("MT - Non e' stato possibile connettersi alla rete", AP_NAME + ".\nControllare credenziali "+ str(e))
        
        try:
            MqttConnection.client = mqtt.Client(CLIENT_NAME, True)
            for retry in range(10):
                try:
                    MqttConnection.client.connect(SERVER, 60)
                    break
                except Exception as e:
                    print("MT - Connettendo al server... Tentativo numero:", retry)
            
            print("MT - Connesso al server", SERVER, "come", CLIENT_NAME)
            MqttConnection.client.subscribe([ [NEEDER_TOPIC,1] ])
            print("MT - Subscribe al topic", NEEDER_TOPIC, "effettuata!")
            #Restituzione del client 
            return MqttConnection.client
            
        except Exception as e:
            print("MT - Errore durante la connessione del server MQTT'", e)
    
# Function used to communicate to the clients reports about pill assumption and the count of pills remaining
    def publishMessage(message): #Send 
        print("MT - Publish effettuata su topic:", RELATIVE_TOPIC, "Messaggio:", message)
        MqttConnection.client.publish(RELATIVE_TOPIC, message, qos = 1, retain = False)
    
    def __init__(self):
        MqttConnection.client = MqttConnection.init()
        MqttConnection.client.loop(MqttConnection.new_news)
    
# Function called when a publish is done on the Needer topic, if it's a JSON procedes with auth and parsing of the function, if correctly specified
    def new_news(client, data):
        message = data['message']
        print("MT - Ricevuto messaggio su topic:", message.topic,  "- dati: ", message.payload)
        try: 
            json_received = json.loads(message.payload)
        except Exception as e:
            print("MT - Received a non-JSON message:", message.payload)
        else:
            print("MT - JSON received:", json_received)
            if MqttConnection.auth(json_received):
                MqttConnection.parse_function(json_received)
    
# This functions ensure that the MQTT message received is directed to this specific device
    def auth(json_received):
        try:
            effs = flash_memory.ExclusiveFlashFileStream.getInstance()
            if(effs == None):
                print("MT - Impossibile ottenere ExclusiveFlashFileStream")
            sleep(100)
            json_local = flash_memory.readFlashJSON(effs)
            if json_local["name"] == json_received["name"] and json_local["pin"] == json_received["pin"] and json_local["pillName"] == json_received["pillName"]:
                print("MT - Autenticazione riuscita")
                return True
            else:
                print("MT - Autenticazione non riuscita")
                return False
        except Exception as e:
            print(e)
    
# This is the fundamental function to execute function to the system.
# By reading the JSON fields 'function' and 'arg0', it understands what to do and how
    def parse_function(json):
        f = json["function"]
        if f == "delete_schedule":
            print("MT - Deleting", json["arg0"], "schedule")
            flash_memory.clearDayFlashJSON(json["arg0"])
        elif f == "set_schedule":
            changes = [json["arg0"]]
            print("MT - Setting new", changes[0][0], "schedule:", changes[0][1])
            if(changes[0][0] == "even" or changes[0][0] == "all"):
                changes.append(["tuesday", changes[0][1]])
                changes.append(["thursday", changes[0][1]])
                changes.append(["saturday", changes[0][1]])
                print(changes)
            if(changes[0][0] == "odd" or changes[0][0] == "all"):
                changes.append(["monday", changes[0][1]])
                changes.append(["wednesday", changes[0][1]])
                changes.append(["friday", changes[0][1]])
                changes.append(["sunday", changes[0][1]])
            flash_memory.overrideFlashJSON(changes)
        elif f == "change_pill":
            print("MT - Changing pill to", json["arg0"])
            flash_memory.overrideFlashJSON([["pillName", json["arg0"]], ["count", 0], ["monday", []], ["tuesday", []], ["wednesday", []], ["thursday", []], ["friday", []], ["saturday", []], ["sunday", []]])
        elif f == "refill_stock":
            print("MT - Refilling stock with", json["arg0"], "pills")
            flash_memory.change_pill_count(json["arg0"])