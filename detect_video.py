# yolov4tiny
import time
import tensorflow as tf

physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
from absl import app, flags, logging
from absl.flags import FLAGS
import core.utils as utils
import core.FeatureDetectors as matching
from core.yolov4 import filter_boxes
from tensorflow.python.saved_model import tag_constants
from PIL import Image
import cv2
import numpy as np
import paho.mqtt.client as mqtt
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

flags.DEFINE_string('framework', 'tf', '(tf, tflite, trt')
flags.DEFINE_string('weights', './checkpoints/yolov4-tiny-416',
                    'path to weights file')
flags.DEFINE_boolean('tiny', False, 'yolo or yolo-tiny')
flags.DEFINE_string('model', 'yolov4', 'yolo-tiny')
flags.DEFINE_integer('size', 416, 'resize images to')
flags.DEFINE_float('iou', 0.45, 'iou threshold')
flags.DEFINE_float('score', 0.25, 'score threshold')
flags.DEFINE_boolean('dont_show', False, 'dont show video output')

redetect_ok = False  # 재인식을 위한 조건 변수
isFirst = False  # YOLO를 이용해 사용자 인식하기 위한 조건변수

ok = True
motor_camera = ' '
buzzer = 'off'
mid = 0  # rectangle 중심좌표
count = 0
tracker = None  # 초기 KCF Tracker는 None
isDetect = False  # 재인식을 위한 조건변수
isGo = False  # 현재 앞으로 가고 있으면 True 아니면 False
mode = 'auto'  # 현재 수동 모드인지 자동 모드인지
object = 'ok' # 장애물 여부

def check_roi(roi):
    (x, y, w, h) = roi
    if x < 0:
        x = 0
    elif x > 480:
        x = 480
    if y < 0:
        y = 0
    elif y > 320:
        y = 320

    if x + w > 480:
        w = 480 - x
    if y + h > 320:
        h = 320 - y

    if w > 240:
        x += (w - 240) / 2
        w = 240
    if h > 180:
        y += (h - 180) / 2
        h = 180

    return (x, y, w, h)


def main(_argv):
    # MQTT 설정
    #broker_address = "172.20.10.6"  #소진
    broker_address = "192.168.0.7"  # nstl_sub
    #broker_address = "192.168.137.27"  #
    client = mqtt.Client()
    config = ConfigProto()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(broker_address, 1883)
    client.loop_start()
    client.on_message = on_message
    client.subscribe("Cam")
    client.subscribe("mode")
    client.subscribe("motor_front")
    client.subscribe("motor_back")
    client.subscribe("motor_object")

    # Yolov4-tiny 설정
    config.gpu_options.allow_growth = True
    cv2.ocl.setUseOpenCL(False)
    session = InteractiveSession(config=config)
    STRIDES, ANCHORS, NUM_CLASS, XYSCALE = utils.load_config(FLAGS)
    input_size = FLAGS.size

    saved_model_loaded = tf.saved_model.load(FLAGS.weights, tags=[tag_constants.SERVING])
    infer = saved_model_loaded.signatures['serving_default']

    # begin video capture
    try:
        #vid = cv2.VideoCapture('http://172.20.10.6:8081/?action=stream')  # motion web streaming - 소진
        vid = cv2.VideoCapture('http://192.168.0.7:8081/?action=stream')  # motion web streaming - nstl_sub
        #vid = cv2.VideoCapture('http://192.168.137.27:8081/?action=stream')  # motion web streaming - 소진1

    except:
        print('error: empty camera!')

    # out = None
    global redetect_ok, ok, mid, motor_camera, buzzer, isFirst, count, tracker, isDetect
    idx = 0  # 저장할 사진 인덱스
    while True:
        return_value, frame = vid.read()

        if return_value:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)  # numpy배열을 Image객체로 바꿈
        else:
            print('Video has ended or failed, try a different video format!')
            break

        if isFirst:  # YOLO로 사람 검출
            # frame_size = frame.shape[:2]
            image_data = cv2.resize(frame, (input_size, input_size))
            image_data = image_data / 255.
            image_data = image_data[np.newaxis, ...].astype(np.float32)

            batch_data = tf.constant(image_data)
            pred_bbox = infer(batch_data)
            for key, value in pred_bbox.items():
                boxes = value[:, :, 0:4]
                pred_conf = value[:, :, 4:]

            boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
                boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
                scores=tf.reshape(
                    pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
                max_output_size_per_class=50,
                max_total_size=50,
                iou_threshold=FLAGS.iou,
                score_threshold=FLAGS.score
            )

            pred_bbox = [boxes.numpy(), scores.numpy(), classes.numpy(), valid_detections.numpy()]
            roi = utils.detect_roi(frame, pred_bbox)
            (a, b, c, d) = roi  # 변경전 좌표 저장
            roi = check_roi(roi)

            if roi[2] and roi[3]:  # 위치 설정 값이 있는 경우
                tracker = cv2.TrackerKCF_create()  # 트래커 객체 생성
                tracker.init(frame, roi)  # Initialize tracker with first frame and bounding box
                user = frame[int(b):int(d + b), int(a):int(c + a)]

                if count == 0:
                    cv2.imwrite('./user/face1.jpg', user)  # 정면 사진 촬영
                count += 1
                if count < 75 * idx:
                    continue
                else:
                    idx += 1
                    path = './user/face' + str(idx) + '.jpg'
                    print(idx)
                    cv2.imwrite(path, user)  # 왼쪽 사진 촬영
                    client.publish('OK', 'camera')
                    if idx == 4:
                        isFirst = False  # 사용자 등록 종료
                        idx = 0

            else:
                continue

        if isDetect:  # Tracking(KCF)
            homography = matching.featureDetect(frame)
            homography = check_roi(homography)

            if tracker is None:
                continue

            if tracker is not None:
                tracker.init(frame, homography)

            if (homography != 0, 0, 0, 0):  # 60%일치하고, box좌표가 존재한다면
                redetect_ok, boxes = tracker.update(frame)  # 새로운 프레임에서 추적 위치 찾기
                (x, y, w, h) = boxes

                if redetect_ok:  # 적당한 크기의 box일 경우
                    # print('재인식끝')
                    isDetect = False  # 재인식 종료
                    client.publish('buzzer', 'off')  # buzzer 종료
                    if mode == 'auto':
                        client.publish('motor_camera', 'motor start')
                else:
                    isDetect = True
                    redetect_ok = False

        # tracker_kcf
        if tracker is None:  # 트래커가 생성 안 된 경우
            cv2.putText(frame, "Cannot detect person",
                        (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2, cv2.LINE_AA)
        else:
            if ok:
                ok, boxes = tracker.update(frame)  # 새로운 프레임에서 추적 위치 찾기
                (x, y, w, h) = boxes
                cv2.rectangle(frame, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 0), 2, 1)
                mid = int(x + (w / 2))

            elif redetect_ok:  # 재인식
                redetect_ok, boxes = tracker.update(frame)  # 새로운 프레임에서 추적 위치 찾기
                (x, y, w, h) = boxes
                cv2.rectangle(frame, (int(x), int(y)), (int(x + w), int(y + h)), (0, 0, 255), 2, 1)  # 사각형 그리기
                mid = int(x + (w / 2))  # 사각형의 중간 좌표

            else:  # 인식이 되지 않는 경우
                isDetect = True  # 재인식 실행
                tracker.clear()  # Tracker 초기화
                tracker = cv2.TrackerKCF_create()  # 트래커 객체 생성

                cv2.putText(frame, "Tracking fail.", (100, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2, cv2.LINE_AA)
                client.publish('buzzer', 'on')  # 부저 실행을 위한 MQTT 값 전송

        result = np.asarray(image)
        cv2.namedWindow("result", cv2.WINDOW_AUTOSIZE)
        result = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        if not FLAGS.dont_show:
            cv2.imshow("result", result)

        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cv2.destroyAllWindows()  # 종료
    # MQTT 종료
    client.loop_stop()
    client.disconnect()
    client.loop_forever()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected OK")
    else:
        print("Bad connection Returned code=", rc)


def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))


def on_message(client, userdata, message):
    global isFirst, tracker, motor_camera, buzzer, mid, isDetect, count, isGo, ok, mode, object
    print("Topic", message.topic, "data", message.payload)
    # print(message.payload)
    if message.topic == 'motor_object':
        if message.payload == b'stop':
            object = 'stop'
        elif message.payload == b'ok':
            object = 'ok'

    if message.topic == 'motor_front':
        if object == 'ok':
            if message.payload == b'back':
                motor_camera = 'back'
                isGo = False
            elif message.payload == b'big_go' or message.payload == b'small_go':
                if mid != 0:  # box의 중간 좌표 값이 존재하지 않음
                    if mid <= 80:
                        motor_camera = 'big_left'  # 큰 좌회전
                    elif mid <= 160:
                        motor_camera = 'left'  # 좌회전
                    elif mid >= 400:
                        motor_camera = 'big_right'  # 큰 우회전
                    elif mid >= 320:
                        motor_camera = 'right'  # 우회전
                    elif message.payload == b'big_go':
                        motor_camera = 'big_straight'  # 직진
                    elif message.payload == b'small_go':
                        motor_camera = 'small_straight'  # 직진
                isGo = True
            elif message.payload == b'stop':
                motor_camera = 'stop'
            elif message.payload == b'wrong':
                motor_camera = 'wrong'
        elif object == 'stop':
            motor_camera = 'stop'
        client.publish('motor_camera', motor_camera)  # 사용자의 위치 MQTT로 전송
    elif message.topic == 'motor_back':
        if isGo is False and message.payload == b'stop':
            motor_camera = 'stop'
            client.publish('motor_camera', motor_camera)  # 사용자의 위치 MQTT로 전송
    else:
        if message.payload == b'ready':  # start 버튼
            isFirst = True
        if message.payload == b'auto mode':
            mode = 'auto'
        elif message.payload == b'manual mode':
            mode = 'manual'
        if message.payload == b'termination mode':
            tracker = None
            isFirst, isDetect = False, False
            ok = True
            motor_camera = ' '
            mid = 0
            buzzer = 'off'
            mid, count = 0, 0
            mode = 'auto'


if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass
