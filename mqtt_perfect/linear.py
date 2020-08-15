# 초음파 센서로부터 go, back, stop 을 받아 모터 속도 조정
# 카메라로부터 left, right 를 받아 모터 방향 조정
# ok 사인도 오는데 이 때는 모터를 건드리지 않음
import paho.mqtt.client as mqtt
import sys, tty, termios, os  
import linear_header as HBridge
import time

speedleft = 0
speedright = 0

# mqtt connect
def on_connect(client, userdata, flags, rc):
    print ("Connected with result coe " + str(rc))
    client.subscribe("buzzer")  # 수동조작

# receive message
def on_message(client, userdata, msg):
    print("Topic: ", msg.topic + '\nMessage: ' + str(msg.payload))
    char = str(msg.payload)
    print(char + "!")
    global speedleft
    global speedright
    if(char == "manual"):  # 수동모드, 양쪽 모터 속도+
        speedleft = 1
        speedright = 1
        HBridge.setMotorLeft(1)
        HBridge.setMotorRight(1)
        time.sleep(1) # If you want linear motor's length, change number.
        HBridge.setMotorLeft(0)
        HBridge.setMotorRight(0)
    elif(char == "auto"):  # 자동모드, 양쪽 모터 속도-
        speedleft = -1
        speedright = -1
        HBridge.setMotorLeft(-100)
        HBridge.setMotorRight(-100)


client = mqtt.Client()  # MQTT Client 오브젝트 생성
client.on_connect = on_connect  # on_connect callback 설정
client.on_message = on_message  # on_message callback 설정

client.connect('localhost', 1883, 60)  # MQTT 서버에 연결
client.loop_forever()
    