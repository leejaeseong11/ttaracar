# vcc : 5v, trig : 16, echo : 13, gnd : gnd
# 카트 뒤 초음파 센서로 앞의 장애을 판단해서 모터를 조정
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO  # RPi.GPIO에 정의된 기능을 GPIO라는 명칭으로 사용
import time  # time 모듈

GPIO.setmode(GPIO.BCM)  # GPIO 이름은 BCM 명칭 사용
GPIO.setup(16, GPIO.OUT)  # Trig, 초음파 신호 전송핀 번호 지정 및 출력지정
GPIO.setup(13, GPIO.IN)  # Echo, 초음파 수신하는 수신 핀 번호 지정 및 입력지정

mqttc = mqtt.Client()  # MQTT Client 오브젝트 생성
mqttc.connect('localhost', 1883)  # MQTT 서버에 연결

print ('Press SW or input Ctrl+C to quit')  # 메세지 화면 출력

try:
    while True:
        GPIO.output(16, False)        
        time.sleep(0.5)

        GPIO.output(16, True)  # 10us 펄스를 내보냄
        time.sleep(0.00001)  # Python에서 이 펄스는 실제 100us 근처가 됨
        GPIO.output(16, False)  # 하지만 HC-SR04 센서는 이 오차를 받아줌

        while GPIO.input(13) == 0:  # echo 핀이 OFF 되는 시점을 시작 시간으로 잡음
             start = time.time()

        while GPIO.input(13) == 1:  # echo 핀이 다시 ON 되는 시점을 반사파 수신시간으로 잡음
            stop = time.time()

        time_interval = stop - start  # 초음파가 수신되는 시간으로 거리를 계산
        distance = time_interval * 17000
        distance = round(distance, 2)

        time.sleep(1)
        print('Back Distance => ', distance, 'cm')
        if distance > 15:  # 거리가 15cm보다 크면 모터에게 ok, 그렇지 않으면 모터 stop
            msg = "ok"
        else:
            msg = "stop"
        mqttc.publish("motor_back", msg)
except KeyboardInterrupt:  # Ctrl-C 입력 시
    GPIO.cleanup()  # GPIO 관련설정 Clear
    print('bye~')
