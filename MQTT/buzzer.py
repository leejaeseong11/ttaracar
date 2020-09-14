# i/o : 24, vcc : vcc, gnd : gnd
# 카메라로부터 부저 on 메시지를 받으면 랜덤한 음의 부저를 울림
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

buzzer = 25
scale = 294

GPIO.setup(buzzer, GPIO.OUT)
p = GPIO.PWM(buzzer, 600)

mode = b'auto mode'

# mqtt connect
def on_connect(client, userdata, flags, rc):
    print("Connected with result coe " + str(rc))
    client.subscribe("buzzer")
    client.subscribe("mode")
    client.subscribe("OK")

# receive message
def on_message(client, userdata, msg):
    try:
        global run, count, mode
        #print("Topic:", msg.topic + ' Message: ' + str(msg.payload))
        p.stop()  # 내던 소리는 일단 멈춤
        
        if msg.payload == b'auto mode' or msg.payload == b'manual mode' or msg.payload == b'termination mode':
            mode = msg.payload
        
        if msg.topic == "OK":
            p.start(50)  # 소리를 냄
            time.sleep(0.5)  # 소리 사이의 간격
            p.stop()
            
        if mode == b'auto mode' and msg.payload == b'on':
            p.start(50)
            
        elif mode == b'termination mode':
            mode = b'auto mode'

        else:
            p.stop()

            
    except KeyboardInterrupt:  # Ctrl-C 입력 시
        p.stop()
        GPIO.cleanup()  # GPIO 관련설정 Clear

client = mqtt.Client()  # MQTT Client 오브젝트 생성
client.on_connect = on_connect  # on_connect callback 설정
client.on_message = on_message  # on_message callback 설정

client.connect('localhost', 1883, 60)  # MQTT 서버에 연결
client.loop_forever()