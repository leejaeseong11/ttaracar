#  카메라 mqtt 미완성
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
from random import *

mqttc = mqtt.Client()  # MQTT Client 오브젝트 생성
mqttc.connect('localhost', 1883)  # MQTT 서버에 연결

try:
    while True:
        tmp = randint(0, 2) # 부저 조정
        if tmp == 0:  # 부저를 울리는 경우
            msg = "on"
            break
        else:  # 부저를 울리지 않는 경우
            msg = "off"
        mqttc.publish("buzzer", msg)
        time.sleep(1)
        print('buzzer : ' + msg)
        
        tmp2 = randint(0, 3)  # 모터 방향 조정
        if tmp2 == 0:  # 좌회전의 경우
            msg2 = "left"
        elif tmp2 == 1:  # 우회전의 경우
            msg2 = "right"
        else:  # 멈추는 경우
            msg2 = "stop"
        mqttc.publish("motor_camera", msg2)
        time.sleep(1)
        print('motor_camera : ' + msg2)
except KeyboardInterrupt:  # Ctrl-C 입력 시
    GPIO.cleanup()  # GPIO 관련설정 Clear
    print('bye~')