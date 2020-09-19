# 초음파 센서로부터 go, back, stop 을 받아 모터 속도 조정
# 카메라로부터 left, right 를 받아 모터 방향 조정
# ok 사인도 오는데 이 때는 모터를 건드리지 않음
import paho.mqtt.client as mqtt
import sys, tty, termios, os
import mdd10a as HBridge
import time

lr_small = 0.55
big_go = 1
small_go = 0.8
back = 0.6

speedleft = 0.0
speedright = 0.0

direction = '' #카메라에서 받는 값
start = ''
mode = 'auto'

# mqtt connect
def on_connect(client, userdata, flags, rc):
    print ("Connected with result coe " + str(rc))
    client.subscribe("motor_camera")  # 카메라
    client.subscribe("mode")
    client.subscribe("buzzer")

    # receive message
def on_message(client, userdata, msg):
    global direction, speedleft, speedright, start, mode
    try:      
        print("Topic: ", msg.topic + ' Message: ' + str(msg.payload))
        
        if msg.payload == b'auto mode':
            time.sleep(2)
            mode = 'auto'
            start = 'motor start'
        if msg.payload == b'manual mode' or msg.payload == b'termination mode':
            mode = 'manual'
        if msg.payload == b'on':
            start = 'motor stop'
        if msg.payload == b'ready':
            mode = 'auto'

        if mode == 'auto':
            if msg.payload == b'motor start':
                start = 'motor start'
        else:
            start = 'motor stop'
        
        if start == 'motor start':
            if msg.topic == 'motor_camera':
                direction = msg.payload
        
            #print(cnt, ': direction = ' , direction , 'action = ', action)
            #print(direction)
            if direction == b'stop': #그냥 정지
                speedleft = 0
                speedright = 0
            elif direction == b'big_straight':
                speedleft = -big_go
                speedright = -big_go
            elif direction == b'small_straight':
                speedleft = -small_go
                speedright = -small_go
            elif direction == b'left':
                speedleft = -lr_small * 1.65
                speedright = -lr_small
            elif direction == b'right':
                speedleft = -lr_small 
                speedright = -lr_small * 1.65
            elif direction == b'big_left':
                speedleft = -lr_small * 1.8
                speedright = -lr_small
            elif direction == b'big_right':
                speedleft = -lr_small 
                speedright = -lr_small * 1.8
            elif direction == b'back':
                speedleft = back
                speedright = back
            elif direction == b'wrong':
                speedleft = speedleft / 5
                speedright = speedright / 5
                
            if speedleft < -1:  
                speedleft = -1
            elif speedleft > 1:
                speedleft = 1
            if speedright > 1:  
                speedright = 1
            elif speedright > 1:
                speedright = 1
            HBridge.setMotorLeft(speedleft)  
            HBridge.setMotorRight(speedright)
        
        else:
            HBridge.setMotorLeft(0)  
            HBridge.setMotorRight(0)

    except KeyboardInterrupt:  # Ctrl-C 입력 시
        HBridge.setMotorLeft(0)
        HBridge.setMotorRight(0)
        GPIO.cleanup()  # GPIO 관련설정 Clear
        
        print('bye~')

client = mqtt.Client()  # MQTT Client 오브젝트 생성
client.on_connect = on_connect  # on_connect callback 설정
client.on_message = on_message  # on_message callback 설정

client.connect('localhost', 1883, 60)  # MQTT 서버에 연결
client.loop_forever()

"""
def test():
    global action,rear, direction, speedleft, speedright, go_back
    #speedleft -= 0.25
    #speedright -= 0.2675
    speedleft -= 1
    print(speedleft)
    speedright -= 1
    print(speedright)

    if speedleft < -1:  
        speedleft = -1
    elif speedleft > 1:
        speedleft = 1
    if speedright > 1:  
        speedright = 1
    elif speedright > 1:
        speedright = 1
    HBridge.setMotorLeft(speedleft)  
    HBridge.setMotorRight(speedright)
def stop():
    speedleft = 0
    speedright = 0
    HBridge.setMotorLeft(speedleft)  
    HBridge.setMotorRight(speedright)


test()
time.sleep(5)
stop()
"""

