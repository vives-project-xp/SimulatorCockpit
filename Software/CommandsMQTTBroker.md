#Commando's om MQTT te versturen
Data binnen halen:
mosquitto_sub -h localhost -t "#" -v
Data versturen:
mosquitto_pub -t cockpit/input/throttle -m "0.6"
mosquitto_pub -t cockpit/input/battery -m "1" of "0"