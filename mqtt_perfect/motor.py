# 초음파 센서로부터 go, back, stop 을 받아 모터 속도 조정
# 카메라로부터 left, right 를 받아 모터 방향 조정
# ok 사인도 오는데 이 때는 모터를 건드리지 않음
import paho.mqtt.client as mqtt
import sys, tty, termios, os  
import mdd10a as HBridge

speedleft = 0
speedright = 0
small = 0.1 # 우회전/좌회전 수치 조정 0~1
big = 0.3 # 큰우회전/큰좌회전 수치 조정 0~1
# mqtt connect
def on_connect(client, userdata, flags, rc):
    print ("Connected with result coe " + str(rc))
    client.subscribe("motor_camera")  # 카메라
    client.subscribe("motor_front")  # 전방 초음파 센서
    client.subscribe("motor_back")  # 후방 초음파 센서

# receive message
def on_message(client, userdata, msg):
    print("Topic: ", msg.topic + '\nMessage: ' + str(msg.payload))
    char = str(msg.payload)
    print(char + "!")
    global speedleft
    global speedright
    if(char == "b'go'"):  # 전진, 양쪽 모터 속도+
        speedleft = speedleft + 0.1
        speedright = speedright + 0.1
        if speedleft > 1:
            speedleft = 1
        if speedright > 1:
            speedright = 1
        HBridge.setMotorLeft(speedleft)  
        HBridge.setMotorRight(speedright)
    elif(char == "b'back'"):  # 후진, 양쪽 모터 속도-
        speedleft = speedleft - 0.1  
        speedright = speedright - 0.1  
        if speedleft < -1:  
            speedleft = -1  
        if speedright < -1:  
            speedright = -1
        HBridge.setMotorLeft(speedleft)
        HBridge.setMotorRight(speedright)
    elif(char == "b'stop'"):  # 정지, 양쪽 모터 속도 0
        if(speedleft < 0 and speedright < 0):  # 후진 중 장애물
            speedleft = 0  
            speedright = 0  
            HBridge.setMotorLeft(speedleft)  
            HBridge.setMotorRight(speedright)
    elif(char == "right"):  # 우회전, 왼쪽 모터+ 오른쪽 모터-
        speedright = speedright - small
        speedleft = speedleft + small
        if speedright < -1:  
            speedright = -1
        if speedleft > 1:
            speedleft = 1
        HBridge.setMotorLeft(speedleft)
        HBridge.setMotorRight(speedright)
    elif(char == "left"):  # 좌회전, 왼쪽 모터- 오른쪽 모터+
        speedleft = speedleft - small
        speedright = speedright + small
        if speedleft < -1:  
            speedleft = -1  
        if speedright > 1:  
            speedright = 1  
        HBridge.setMotorLeft(speedleft)  
        HBridge.setMotorRight(speedright)
    elif (char == "big_right'"):  # 큰우회전, 왼쪽 모터+ 오른쪽 모터-
        speedright = speedright - big
        speedleft = speedleft + big
        if speedright < -1:
            speedright = -1
        if speedleft > 1:
            speedleft = 1
        HBridge.setMotorLeft(speedleft)
        HBridge.setMotorRight(speedright)
    elif (char == "big_left"):  # 큰좌회전, 왼쪽 모터- 오른쪽 모터+
        speedleft = speedleft - big
        speedright = speedright + big
        if speedleft < -1:
            speedleft = -1
        if speedright > 1:
            speedright = 1
        HBridge.setMotorLeft(speedleft)
        HBridge.setMotorRight(speedright)

client = mqtt.Client()  # MQTT Client 오브젝트 생성
client.on_connect = on_connect  # on_connect callback 설정
client.on_message = on_message  # on_message callback 설정

client.connect('localhost', 1883, 60)  # MQTT 서버에 연결
client.loop_forever()
