import math
import threading
import time
import numpy as np
import torch
import pynput.mouse
from pynput.mouse import Listener

from utils.augmentations import letterbox
from ultralytics.utils.plotting import Annotator
from models.common import DetectMultiBackend
from utils.general import (
    cv2,
    non_max_suppression,
    scale_boxes,
    xyxy2xywh,
)
from utils.torch_utils import select_device, smart_inference_mode

from ScreenShot import screenshot
from SendInput import *

x1_pressed = False

def mouse_click(x, y, button, pressed):
    global x1_pressed
    if pressed and button==pynput.mouse.Button.x1:
        print('開始')
        x1_pressed=True
    elif not pressed and button==pynput.mouse.Button.x1:
        print('關閉')
        x1_pressed=False

def mouse_listener():
    with Listener(on_click=mouse_click) as listener:
        listener.join()

@smart_inference_mode()
def run():
    global x1_pressed
    # Load modelS
    #device = torch.device('cpu') #用cpu
    device = torch.device('cuda:0')
    model = DetectMultiBackend(weights=r'W:\ntou\pro\code\yolov5\runs\train\exp7\weights\best.pt', device=device, dnn=False, data=False, fp16=True)

    #讀取螢幕截圖
    while True:
        im = screenshot()
        im0 = im
        #修改圖片

        im = letterbox(im,(640,640),stride=32,auto=True)[0]
        im = im.transpose((2,0,1))[::-1] #HWC to CHW,BGR to RGB
        im = np.ascontiguousarray(im)

        im = torch.from_numpy(im).to(model.device)
        im = im.half() if model.fp16 else im.float()  # auint8 to fp16/32
        im /= 255  # 0 - 255 to 0.0 - 1.0
        if len(im.shape) == 3:
            im = im[None]  # expand for batch dim

        #推理
        pred = model(im, augment=False, visualize=False)
        #非極大值抑制
        pred = non_max_suppression(pred, conf_thres=0.6, iou_thres=0.45, classes=0, max_det=1000)


        # Process predictions
        for i, det in enumerate(pred):  # per image
            annotator=Annotator(im0, line_width=1)
            if len(det):
                distance_list=[]
                target_list=[]
                # Rescale boxes from img_size to im0 sizeS
                det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()
                # Write results
                for *xyxy, conf, cls in reversed(det): #處理每個目標
                    xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4))).view(-1).tolist()  # normalized xywh
                    line = cls, *xywh, conf
                    X = xywh[0] - 320
                    Y = xywh[1] - 320

                    distance = math.sqrt(X**2 + Y**2)
                    xywh.append(distance)
                    annotator.box_label(xyxy, label=f'[{int(cls)}Distance:{round(distance, 2)}]', color=(34,139,34), txt_color=(0,191,255))

                    distance_list.append(distance)
                    target_list.append(xywh)

                target_info = target_list[distance_list.index(min(distance_list))]
                if x1_pressed:
                    mouse_xy(int(target_info[0]-320),int(target_info[1]-320))
                    time.sleep(0.004)
                #主動延遲


            im0 = annotator.result()
            cv2.imshow("window", im0)
            cv2.waitKey(1)

if __name__ == "__main__":
    threading.Thread(target=mouse_listener).start()
    run()