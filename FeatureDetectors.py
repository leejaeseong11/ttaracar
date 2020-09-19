import cv2
import numpy as np

def featureDetect(frame): #Feature Matching을 통한 사용자 재인식

    MIN_MATCH = 11 #최소 매칭점 개수
    detector = cv2.ORB_create(1000) #최대 Feature 수 = 1000
    FLANN_INDEX_LSH = 6
    index_params = dict(algorithm=FLANN_INDEX_LSH,
                        table_number=6,
                        key_size=12,
                        multi_probe_level=1)
    search_params = dict(checks=32)
    matcher = cv2.FlannBasedMatcher(index_params, search_params)
    idx = 0 # 등록된 사용자와 매칭

    while idx < 4:
        try:
            idx += 1
            #image 불러오기
            path = r"./user/face" + str(idx) + ".jpg"
            img1 = cv2.imread(path, 1)
            img2 = frame

            # 흑백 변환
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

            # 키포인트와 디스크립터 추출
            kp1, desc1 = detector.detectAndCompute(gray1, None)
            kp2, desc2 = detector.detectAndCompute(gray2, None)

            # k=2로 knnMatch
            matches = matcher.knnMatch(desc1, desc2, 2)

            # 이웃 거리의 75%로 좋은 매칭점 추출---②
            ratio = 0.75
            good_matches = [m[0] for m in matches \
                            if len(m) == 2 and m[0].distance < m[1].distance * ratio]

            # 좋은 매칭점 최소 갯수 이상 인 경우
            if len(good_matches) > MIN_MATCH:
                # 좋은 매칭점으로 원본과 대상 영상의 좌표 구하기 ---③
                src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches])
                dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches])
                # 원근 변환 행렬 구하기 ---⑤
                mtrx, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                accuracy = float(mask.sum()) / mask.size
                print("accuracy: %d/%d(%.2f%%)" % (mask.sum(), mask.size, accuracy))

                if mask.sum() > MIN_MATCH:  # 정상치 매칭점 최소 갯수 이상 인 경우

                    # 원본 영상 좌표로 원근 변환 후 영역 표시  ---⑦
                    h, w, = img1.shape[:2]

                    pts = np.float32([[[0, 0]], [[0, h - 1]], [[w - 1, h - 1]], [[w - 1, 0]]])
                    dst = cv2.perspectiveTransform(pts, mtrx)

                    homography = cv2.boundingRect(dst)

                    print(accuracy)
                    if accuracy > 0.65: # ?% 이상이면 반복문 종료
                        return homography
        except:
            continue

    return 0,0,0,0

