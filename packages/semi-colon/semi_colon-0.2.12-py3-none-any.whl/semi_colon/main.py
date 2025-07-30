import math
import numpy as np
import matplotlib.pyplot as plt
import urllib.request, os
from urllib.parse import urlparse
import zipfile, tarfile, gzip


def imshows(imgs, rows=1, cols=None, bgr=True, figsize=None, axis=False):
  #모든 imgs는 zip 형태가 되게 강제한다.
  if isinstance(imgs, np.ndarray): #NumPy 1개
    size = 1
    imgs = zip([''], [imgs])
  elif isinstance(imgs, (list, tuple)): #List, Tuple
    size = len(imgs)
    imgs = zip(['' for _ in imgs], imgs)
  elif isinstance(imgs, dict): #Dict
    size = len(imgs)
    imgs = imgs.items()
  else:
    raise Exception(f'imshows:Not supported image type:{type(imgs)}')

  #행열 설정, 1행이면 n열, 행이 여러개면 열은 이미지 수/행으로 설정
  if rows == 1:
    cols = size  
  elif cols== None:
    cols = math.ceil(size/rows)

  #전체 이미지 표시
  if figsize:
    plt.figure(figsize=figsize)

  for i , (title, img) in enumerate(imgs, start=1):
    plt.subplot(rows, cols, i)
    plt.title(title)
    if img.ndim == 2:
        plt.imshow(img, cmap='gray')
    elif img.ndim == 3:
        if bgr:
            plt.imshow(img[:,:,::-1])
        else:
            plt.imshow(img)
    if axis == False:
      plt.xticks([]); plt.yticks([])
  plt.show();

def getImage(name, dir=None):
  url = f'https://github.com/dltpdn/download/blob/master/img/{name}?raw=true'
  return download(url, dir)

def download(url, dir=None, file_name=None, extract=False):
  if file_name is None:
    parsed = urlparse(url)
    path = parsed.path

    if parsed.netloc == 'github.com':
      split_str = 'master/'
      if split_str in parsed.path:
        path = path.split(split_str, 1)[-1]  # 'master/' 이후 부분 추출
      if not dir:
        dir = os.path.dirname(path)

    if not dir:
      dir='.'

    if not file_name:
        file_name = os.path.basename(path)
  os.makedirs(dir, exist_ok=True)

  to=os.path.join(dir, file_name)
  try:
    urllib.request.urlretrieve(url, to)
  except:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as res:
      with open(to, 'wb') as outfile:
            outfile.write(res.read())
   
  print(f"{to} 파일이 다운로드되었습니다.")

  if extract:
    ext = os.path.splitext(to)[-1]

    if '.zip' == ext :
      with zipfile.ZipFile(to, 'r') as zip:
        ret = zip.extractall(dir)
        print(f'압축풀기:{to}, {ret}')
    elif '.tar' == ext or '.tgz' == ext:
      with tarfile.open(to) as tar:
        tar.extractall(dir)
        
  return to