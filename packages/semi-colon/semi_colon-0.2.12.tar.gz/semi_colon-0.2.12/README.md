
* **semi-colon** is a utility module designed for use in Computer Vision, Data Science, Machine Learning, and Deep Learning. 
* This document was written in Korean. If necessary, machine translate it into your preferred language.
* **semi-colon**은 컴퓨터 비전, 데이터 과학, 머신러닝, 딥러닝에 사용하기 좋게 만든 유틸리티 모듈입니다.

# semi_colon
## `load_boston()`

* scikit-learn에서 더 이상 제공하지 않는 `sklearn.datasets.load_boston()`과 동일한 기능입니다.
* 당연하게도 저는 인종차별에 동의하지 않습니다.

##  `imshows(imgs, rows=1, cols=None, bgr=True, figsize=None, axis=False)`
* matplotlib을 이용해서 `imgs`에 전달한 이미지를 한 번에 표시합니다.  
* `imgs` : 표시할 이미지
    * `imgs`는 다음 중 하나가 될 수 있습니다.
        * 하나의 NumPy Array, 예) `img = cv2.imread('tkv.jpg)`
        * List 또는 Tuple에 들어 있는 NumPy Array, 예) `[img1, img2]`, `(img1, img2)`
        * 제목을 key로 하고 NumPy Array를 value로 하는 Dict, 예) `{'img1':img1, 'img2':img2}`
    * matplotlib은 image의 값을 자동으로 0~255로 정규화해서 표시합니다. 따라서 이미지의 dtype은 uint8은 물론이고 소수점이 있는 float 계열도 표시에 문제가 없지만 warning 메시지가 표시될 수 있습니다.
* `rows` : 몇 행으로 표시할 지 정수로 지정합니다.
* `cols` : 몇 열로 표시할 지 정수로 지정합니다. 생략하면 `imgs`의 갯수에 따라 자동으로 결정합니다.
* `bgr` : `imgs`의 컬러 채널 순서를 지정합니다.`True`이면 BGR, `False`이면 RGB입니다. gray 컬러(2D) 일때는 무시하고 자동으로 gray 컬러로 출력합니다.
* `figsize` : 표시할 영역의 크기를 (width,height) 순으로 지정합니다.
* `axis` :  축 눈금 표시 여부
* example
```python
img = cv2.imread('tkv.jpg')
imshows(img)
imshows((img, img))
imshows({'first':img, 'second':img})
```

## `getImage(name, dir=None)`
* https://github.com/dltpdn/download/tree/master/img 에서 `name`에 해당하는 이미지를 다운로드 합니다.
* 다운로드 위치는 `dir`를 지정하지 않으면  `./img/` 로 고정되어 있습니다. `./img` 디렉토리가 없으면 자동으로 생성합니다.

## `download(url, dir=None, file_name=None, extract=False)`
* `url`로 부터 파일을 `dir`에 다운로드 합니다.
* `url`이 github.com 이라면, url의 `master/`를 기준으로 자동으로 다운로드 되는 경로와 파일이름이 결정됩니다.
* `extract=True` 인 경우 zip, tar 파일은 압축을 해제합니다.

## `digit_split(image, size=None, flatten=False, border=0, inverse=True)`
사용자가 직접 작성한 숫자 손글씨 이미지에서 각 숫자를 원하는 크기로 분할해서 반환합니다.
* `image`에 포함된 각각의 숫자를 개별 이미지로 분할해서 리스트에 담아 반환합니다.
* `size`는 반환 이미지의 크기를 지정할 수 있습니다.
* `flatten=True`은 (1, n) 형태로 변환해서 반환합니다.
* `border`는 반환하는 이미지의 테두리 여백을 지정합니다.
* `inverse`는 흰색과 검정색을 반전합니다.

## `draw_bbox(img, x1, y1, x2, y2, text=None, txt_color=(255,255,255), bb_color=None, thickness=2)`
* `img`에 주어진 `x1,y1,x2,y2` 좌표로 bounding box를 표시하고 사본을 반환합니다.
* `text` : bounding box의 좌상단에 `text`를 표시합니다. 클래스 이름과 확률 값을 표시하는 용도로 쓰면 좋습니다.
* `txt_color` : `text`를 표시할 때 사용할 컬러 값입니다.
* `bb_color` : bounding box 테두리 선 컬러 값입니다. 생략하면 무작위로 선택합니다.
* `thickness` :  bounding box 테두리 선의 두께 값입니다.

## `get_iou(pred, gt)`
* `pred`, `gt`로 IoU(Intersection of Union)를 계산해서 반환합니다.
----
# semi_colon.colab
Google colab에서만 동작하는 함수들을 포함하는 패키지 입니다. OpenCV headless 버전에서 동작하지 않는 GUI 상호작용 기능을 colab의 notebook 환경에서 유사하게 동작하게 했습니다. 이 패키지는 `google.colab` 관련 패키지에 종속성이 있어서 colab이외의 환경에서는 동작하지 않으니 코드에 `import` 구문을 넣는데 유의하세요.
## `setMouseCallback(img, onmouse=None)`
* **_이 함수는 Google Colab에서만 동작합니다._**
* `cv2.setMouseCallBack()`함수를 Google Colab에서 사용 할 수 있게 수정했습니다.
* `img`를 출력으로 표시하고 마우스 이벤트가 발생하면 `onmouse` 함수를 호출합니다.
* `onmouse`에 지정할 함수의 parameter는 `cv2.setMouseCallback()`의 `callback(event, x, y, flag, param)` 함수와 형식이 동일합니다.
* callback에 전달되는 `param`은 기능이 없고 언제나 `None`입니다.

## `selectROI(img, callback)`
* **_이 함수는 Google Colab에서만 동작합니다._**
* `cv2.selectROI()`함수를 Google Colab에서 사용 할 수 있게 수정했습니다.
* `img`를 출력으로 표시하고 마우스로 ROI 영역을 선택하고 나면 `callback(x,y,w,h)`를 호출 합니다.
