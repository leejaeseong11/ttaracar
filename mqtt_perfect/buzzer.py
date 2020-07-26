# i/o : 24, vcc : vcc, gnd : gnd
# 카메라로부터 부저 on 메시지를 받으면 랜덤한 음의 부저를 울림
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
from random import *

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

buzzer = 24
scale = [261, 294, 329, 349, 392, 440, 493, 523]  # 도레미파솔라시도

GPIO.setup(buzzer, GPIO.OUT)
p = GPIO.PWM(buzzer, 600)
num = randint(0, 8)  # 랜덤한 음 하나를 설정

# mqtt connect
def on_connect(client, userdata, flags, rc):
    print("Connected with result coe " + str(rc))
    client.subscribe("buzzer")

# receive message
def on_message(client, userdata, msg):
    print("Topic: ", msg.topic + '\nMessage: ' + str(msg.payload))
    p.stop()  # 내던 소리는 일단 멈춤
    print(str(msg.payload))
    if str(msg.payload) == "b'on'":  # on 메시지를 받는 경우
        p.start(50)  # 소리를 냄
        p.ChangeFrequency(scale[num])
        time.sleep(0.5)  # 소리 사이의 간격
    else:
        p.stop()

client = mqtt.Client()  # MQTT Client 오브젝트 생성
client.on_connect = on_connect  # on_connect callback 설정
client.on_message = on_message  # on_message callback 설정

client.connect('localhost', 1883, 60)  # MQTT 서버에 연결
client.loop_forever()
