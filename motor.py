# 초음파 센서로부터 go, back, stop 을 받아 모터 속도 조정
# 카메라로부터 left, right 를 받아 모터 방향 조정
# ok 사인도 오는데 이 때는 모터를 건드리지 않음
import paho.mqtt.client as mqtt
import sys, tty, termios, os  
import mdd10a as HBridge
import time

lr_small = 0.005 # 우회전/좌회전 수치 조정 0~1
lr_big = 0.05 # 큰우회전/큰좌회전 수치 조정 0~1
go_back = 0.3 

speedleft = 0.0
speedright = 0.0
#speedplus = 0.07 * small

action = '' #직진, 후진, 정지
rear = '' #후방 초음파
direction = '' #카메라에서 받는 값
start = ' '
# mqtt connect
def on_connect(client, userdata, flags, rc):
    print ("Connected with result coe " + str(rc))
    client.subscribe("motor_camera")  # 카메라
    client.subscribe("motor_front")  # 전방 초음파 센서
    client.subscribe("motor_back")  # 후방 초음파 센서
    client.subscribe("/motor/start")

    # receive message
def on_message(client, userdata, msg):
    global action,rear, direction, speedleft, speedright, speedplus, start

    try:
        print("Topic: ", msg.topic + '\nMessage: ' + str(msg.payload))
        if msg.topic == "/motor/start/":
            if msg.payload == b'motor start':
                start = 'motor start'
        if start == 'motor start':
            if msg.topic == 'motor_camera':
                direction = msg.payload
            elif msg.topic == 'motor_front':
                action = msg.payload
            elif msg.topic == 'motor_back':
                rear = msg.payload
            
            print('direction = ' , direction , 'action = ', action)
            if direction == b'stop' or rear == b'stop': #그냥 정지
                speedleft = 0
                speedright = 0
            elif action == b'go':
                if direction == b'straight':
                    speedleft = -go_back
                    speedright = -go_back
                elif direction == b'left':
                    speedleft = -lr_small
                    speedright = lr_small
                elif direction == b'right':
                    speedleft = lr_small
                    speedright = -lr_small
                elif direction == b'big_left':
                    speedleft -= lr_big
                    speedright += lr_big
                elif direction == b'big_right':
                    speedleft += lr_big
                    speedright -= lr_big
            elif action == b'ok':
                pass
            elif action == b'back':
                speedleft = 0
                speedright = 0
                if direction == b'straight':
                    speedleft = go_back
                    speedright = go_back
                elif direction == b'right':
                    speedleft = lr_small
                    speedright = -lr_small
                elif direction == b'left':
                    speedleft = -lr_small
                    speedright = lr_small
                elif direction == b'big_right':
                    speedleft += lr_big
                    speedright -= lr_big
                elif direction == b'big_left':
                    speedleft -= lr_big
                    speedright += lr_big
            
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
            
            direction = ' '
            #char = str(msg.payload)
            #print(char + "!")
          
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
    speedleft -= 0.8
    print(speedleft)
    speedright -= 0.8
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