# general board setup
import machine, time, dht
import network, ntptime

from umqtt.simple2 import MQTTClient
import ubinascii

# configure GPIO pins
RedLED = machine.Pin(16, machine.Pin.OUT)
RedLED.value(0)

GreenLED = machine.Pin(17, machine.Pin.OUT)
GreenLED.value(0)

AM2302 = dht.DHT22(machine.Pin(14))

# define Wi-Fi settings
wifiSSID = 'your-WiFi-SSID-goes-here'
wifiPasswd = 'your-WiFi-password-goes-here'

# Please generate a uniquie UUID at: https://www.uuidgenerator.net/ and replace the one below
# Don't forget the single quotations start and finish!
deviceUUID = '1116fa09-973c-4fa3-aff1-3f9859c819ff'

# define MQTT settings
client_id = ubinascii.hexlify(deviceUUID)
topic = bytes(deviceUUID, 'utf-8')

mqtt_broker = 'public.mqtthq.com'
mqtt_port = 1883

# define function for setting up Wi-Fi network
def wifi_connect():
    wifi = network.WLAN(network.STA_IF)  # create our 'wifi' network object
    wifi.active(True)  # turn on the Wi-Fi hardware

    # if not connected ...
    while wifi.isconnected() == False:

        GreenLED.value(1)  # turn Green LED ON
        print('trying WiFi connection ', wifiSSID)  # print 'trying..' message to Shell

        wifi.connect(wifiSSID, wifiPasswd)  # try connecting to wifi

        time.sleep(1)  # wait 1 second

        GreenLED.value(0)  # turn Green LED OFF

        time.sleep(2)  # wait 2 second

    # if connected ...
    GreenLED.value(1)  # turn Green LED ON
    print('WiFi connection successful')  # print 'WiFi connection successful' message to Shell
    print(wifi.ifconfig())  # print WiFi network settings (inc. IP Address) to Shell


# define function to synchronise local clock with NTP time
def sync_to_NTP():
    ntpConnected = 0   # initialise an 'ntpConnected' variable to hold status, set it to

    while ntpConnected == 0:   # while not connected to NTP network ...

        try:
            print('Trying to Sync with NTP servers')   # print debug message to Shell
            ntptime.settime()   # set localtime to NTP time
            ntpConnected = 1   # set ntpConnected status to 1

        except:
            print ('NTP error')   # print debug message to Shell
            ntpConnected = 0   # set ntpConnected status to 0

    print('Local time synchronised: ', get_time_str()) # print the new localtime as a string


# define function for getting local time as string
def get_time_str():
    my_time = time.localtime()   # get 'localtime' and store it in a variable 'my_time'
    my_time_string = '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(my_time[0], my_time[1], my_time[2], my_time[3], my_time[4], my_time[5])   # convert localtime to a formatted text string 'my_time_string'
    return my_time_string  # return the formatted string


# define function to connect to MQTT broker
def mqtt_connect():
  global client_id, mqtt_broker, mqtt_port   # use the global variables: client_id, mqtt_broker, mqtt_port

  print('client_id ' + str(client_id) + ' topic ' + topic.decode("utf-8"))
  client = MQTTClient(client_id, mqtt_broker, mqtt_port)  # create MQTT client using our MQTT settings

  # initialise our local variables (used to manage the connection process)
  broker_connected = 0   # broker connection status register
  connect_attempt = 1    # keep track of the number of connection attempts
  max_con_attempts = 5   # set the maximum number of connection attempts - we'll reboot after this number of attempts

  while (connect_attempt <= max_con_attempts) and broker_connected == 0:

      print('Connecting to MQTT broker:  '+mqtt_broker+', publishing to topic: ' + topic.decode("utf-8") + ', Attempt No. :' + str(connect_attempt))

      try:
          client.connect()   # attempt to connect to the MQTT broker

          print("Connection successful")   # if successful, send success message to Shell
          broker_connected = 1             # set broker connection status register to 1

      except Exception as X:
          print("Connection attempt failed: " + str(X))   # if NOT successful, send debug message to Shell

          if connect_attempt < max_con_attempts:      # if current connection attempt is less than max connection attempts ...
              connect_attempt = connect_attempt + 1   # increment the connection_attempt count
              time.sleep(2)                           # wait 2 seconds before re-attempting a connection

          else:
              print('Failed to connect to MQTT broker after ' + str(connect_attempt) + ' attempts. Rebooting...')  # if max_con_attempts reached ...
              time.sleep(2)     # wait 2 seconds
              machine.reset()   # reset the ESP32 ... forcing a full re-connection process including Wi-Fi

  return client   # if connection successful, return the client object
