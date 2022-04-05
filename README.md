# ttaracar

## MQTT

컴퓨터와 IoT 모듈이 함께 통신하기 위한 프로토콜로 HTTP의 클라이언트-서버 구조로 이루어지는 것이 아닌, Broker, Publisher, Subscriber 구조로 이루어짐.
Publisher는 Topic을 발행(publish) 하고, Subscriber는 Topic을 구독(subscribe).
Broker는 이들을 중계하는 역할을 하며, 단일 Topic에 여러 Subscriber가 구독할 수 있기 때문에, 1:N 통신 구축에도 매우 유용
최소한의 전력과 패킷량으로 통신하기 때문에 IOT와 모바일 어플리케이션 등의 통신에 매우 적합

- buzzer.py: 부저 컨트롤
- 리니어 모터 관련
  - linear_header.py: 모터의 움직임을 제어하기 위한 함수 정의
  - linear.py: MQTT payload에 따라 움직임 조절
- 모터 관련
  - mdd10a.py: 모터의 방향 및 속도 조절을 위한 함수 정의
  - motor.py: 카메라에 따른 방향 및 초음파 센서에 따른 거리에 따라 움직임 조절
- 초음파 센서 관련
  - ultrasonic_wave_front.py: 카트 앞 거리 측정
  - ultrasonic_wave_back.py: 카트 뒤 거리 측정
  - ultrasonic_wave_object.py: 카트 앞 하단 장애물 감지

## OpenCV 및 YOLOv3 (tensorflow)

- detect_video.py: 연결된 카메라로부터 YOLO를 이용해 사람을 인식하여 이미지를 저장
- object_tracker.py
  - 저장된 사람 이미지를 바탕으로 템플릿 매칭으로 사람을 찾음
  - 실시간 스트리밍 프로토콜(RSTP)를 통해 카메라 영상을 실시간으로 받아옴

## Screen

C# 기반으로 라즈베리파이와 연결한 모니터에서 사용할 수 있는 GUI 구성

---

### 개선점

- YOLO 모델에 저장한 사람 이미지를 학습시켜서 시간이 지날수록 매칭을 더 정확하게 할 수 있을지
- 초음파 센서 특성상 값이 튀는 경우가 발생하여 카트의 제어가 이상해지는데, 다른 센서를 사용하더라도 정확하게 방지할 수 있을지
- 영상을 전달하고 처리하는 속도를 단축시켜 delay 없이 realtime으로 처리할 수 있을지
