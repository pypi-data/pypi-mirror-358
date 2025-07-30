
# coding: utf-8


import cv2
import numpy as np

def digit2data(src, size=(8,8), flatten=False, border=0):
    h, w = src.shape[:2]
    square = src
    # 정사각형 형태로 만들기
    if h > w:
        pad = (h - w)//2
        square = np.zeros((h, h), dtype=np.uint8)
        square[:, pad:pad+w] = src
    elif w > h :
        pad = (w - h)//2
        square = np.zeros((w, w), dtype=np.uint8)
        square[pad:pad+h, :] = src
    px = np.zeros(size, np.uint8)
    content = size
    if border != 0 :
        content = (size[0] - (border*2), size[1] - (border*2))
        px[border:-border, border:-border] = cv2.resize(square, content, interpolation=cv2.INTER_AREA)
    else:
        px[:, :] = cv2.resize(square, content, interpolation=cv2.INTER_AREA)
    if flatten:
        px = px.reshape((1,-1))
    return px 

def digit_split(image, size=None, flatten=False, border=0, inverse=True):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    (major, minor, _ )= cv2.__version__.split(".")
    if int(major) > 3 :
        contours, hirachy = cv2.findContours(th, cv2.RETR_EXTERNAL, 
                                        cv2.CHAIN_APPROX_SIMPLE)
    else :
        _, contours, hirachy = cv2.findContours(th, cv2.RETR_EXTERNAL, 
                                        cv2.CHAIN_APPROX_SIMPLE)
    digits = {}
    #numbers = []
    for c in contours:
        # 컨투어를 감싸는 외접 사각형으로 숫자 영역 좌표 구하기 ---⑦
        (x, y, w, h) = cv2.boundingRect(c)    
        # 외접 사각형의 크기가 너무 작은것은 제외 ---⑧
        if w >= 5 and h >= 25:
            # 숫자 영역만 roi로 확보하고 사각형 그리기 ---⑨
            roi = gray[y:y + h, x:x + w]
            #numbers.append(roi)
            digits[x] = roi
    numbers = [v for k, v in sorted(digits.items())] # 왼쪽 부터 순서대로 정렬
        
    if inverse:
        for i, n in enumerate(numbers):
            numbers[i] = 255- n  # 반전
        
    if size is None:
        return numbers
    else:
        for i, n in enumerate(numbers):
            numbers[i] = digit2data(n, size, flatten, border)
        return numbers
