import cv2
import numpy as np

def draw_bbox(img, x1, y1, x2, y2, text=None, txt_color=(255,255,255), bb_color=None, thickness=2, font_size=0.7):
  draw = img.copy()
  font = cv2.FONT_HERSHEY_DUPLEX
  if bb_color is None:
    bb_color = np.random.randint(0, 200, 3).tolist()
  #bbox 그리기
  cv2.rectangle(draw, (x1, y1), (x2, y2), bb_color, thickness)
  if text:
    #text 크기 구하기
    txt_w, txt_h = cv2.getTextSize(text, font, font_size, 1)[0]
    #text 영역 그리기
    cv2.rectangle(draw, (x1, y1), (x1+txt_w+4, y1+txt_h+4), bb_color, thickness=-1)
    #text 출력
    cv2.putText(draw, text, (x1, y1+txt_h), font, font_size, color=txt_color)
  return draw


def get_iou(pred, gt):
  x1 = np.maximum(pred[0], gt[0]) #좌상단 x
  y1 = np.maximum(pred[1], gt[1]) #좌상단 y
  x2 = np.minimum(pred[2], gt[2]) #우하단 x
  y2 = np.minimum(pred[3], gt[3]) #우하단 y

  pred_area = (pred[2] - pred[0]) * (pred[3] - pred[1])
  gt_area = (gt[2] - gt[0]) * (gt[3] - gt[1])
  intersection = np.maximum(x2 - x1, 0) * np.maximum(y2 - y1, 0)
  union = pred_area + gt_area - intersection
  iou = intersection / union
  return iou