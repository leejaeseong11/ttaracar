#!/bin/bash
python3 /home/pi/Desktop/MQTT/motor.py &
python3 /home/pi/Desktop/MQTT/ultrasonic_wave_back.py &
python3 /home/pi/Desktop/MQTT/linear.py &
python3 /home/pi/Desktop/MQTT/buzzer.py &
python3 /home/pi/Desktop/MQTT/ultrasonic_wave_front.py
