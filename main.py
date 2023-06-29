# connect to wifi
wifi_connect()

# wait 5 seconds for network to settle
time.sleep(5)

# synchronise local clock with NTP time
sync_to_NTP()

# wait 1 second
time.sleep(1)

# set up MQTT connection and subscribe
client = mqtt_connect()


# this is the main program loop
while True:

  RedLED.value(1)   # turn RedLED ON

  AM2302.measure()  # start AM2302 measurement

  RedLED.value(0)   # turn RedLED OFF

  tempC = AM2302.temperature()   # get temperature (Celsius) from AM2302
  humidity = AM2302.humidity()   # get humidity from AM2302

  JSONstring = '{"TimeUTC":"'+get_time_str()+'","TemperatureC":'+str(tempC)+',"Humidity":'+str(humidity)+'}'
  print("PUBL " + topic.decode("utf-8") + " " + JSONstring)

  MQTTmsg = bytes(JSONstring, 'utf-8')

  try:
    client.publish(topic, MQTTmsg)

  except Exception as X:
    print("Can not publish message (error " + str(X) + ") - reconnecting")
    mqtt_connect()

  time.sleep(30)    # wait here
