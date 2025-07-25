# -*- coding: utf-8 -*-
"""
-------------------------------------------------
Project Name: yolov5
File Name: window.py
Author: daiwei
Create Date: 2024/05/25
Description：图形化界面，可以检测摄像头、视频和图片文件
-------------------------------------------------
"""
# 应该在界面启动的时候就将模型加载出来，设置tmp的目录来放中间的处理结果
import shutil
import PyQt5.QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import threading
import argparse
import os
import sys
from pathlib import Path
import cv2
import torch
import torch.backends.cudnn as cudnn
import os.path as osp
import time  # 确保导入了time模块
from FaceAPI import Recognize
from FaceAPI import compre_face_base_url
from FaceAPI import api_key
from Dataset import Dataset
# 调用实现人脸识别绑定后才进行多目标识别

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from models.common import DetectMultiBackend
from utils.datasets import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams
from utils.general import (LOGGER, check_file, check_img_size, check_imshow, check_requirements, colorstr,
                           increment_path, non_max_suppression, print_args, scale_coords, strip_optimizer, xyxy2xywh)
from utils.plots import Annotator, colors, save_one_box
from utils.torch_utils import select_device, time_sync


# 添加一个关于界面
# 窗口主类
class MainWindow(QTabWidget):
    # 基本配置不动，然后只动第三个界面
    def __init__(self):
        # 初始化界面
        super().__init__()
        self.setWindowTitle('Target&Face detection system ')
        self.resize(1200, 800)
        self.setWindowIcon(QIcon("images/UI/lufei.png"))
        # 图片读取进程
        self.output_size = 480
        self.img2predict = ""
        self.device = '0'
        # # 初始化视频读取线程
        self.vid_source = '0'  # 初始设置为摄像头
        self.stopEvent = threading.Event()
        self.webcam = True
        # 放置权重文件 初始权重文件用于检测外勤人员
        self.model = self.model_load("runs/train/exp/weights/best.pt",
                                     device=self.device)  # todo 指明模型加载的位置的设备
        self.initUI()
        self.reset_vid()

    '''
    ***模型初始化***
    '''
    @torch.no_grad()
    def model_load(self, weights="",  # model.pt path(s)
                   device='',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
                   half=False,  # use FP16 half-precision inference
                   dnn=False,  # use OpenCV DNN for ONNX inference
                   ):
        device = select_device(device)
        half &= device.type != 'cpu'  # half precision only supported on CUDA
        device = select_device(device)
        model = DetectMultiBackend(weights, device=device, dnn=dnn)
        stride, names, pt, jit, onnx = model.stride, model.names, model.pt, model.jit, model.onnx
        # Half
        half &= pt and device.type != 'cpu'  # half precision only supported by PyTorch on CUDA
        if pt:
            model.model.half() if half else model.model.float()
        print("模型加载完成!")
        return model

    '''
    ***界面初始化***
    '''
    def initUI(self):
        # 图片检测子界面
        font_title = QFont('楷体', 16)
        font_main = QFont('楷体', 14)
        # 图片识别界面, 两个按钮，上传图片和显示结果
        img_detection_widget = QWidget()
        img_detection_layout = QVBoxLayout()
        img_detection_title = QLabel("图片识别功能")
        img_detection_title.setFont(font_title)
        mid_img_widget = QWidget()
        mid_img_layout = QHBoxLayout()
        self.left_img = QLabel()
        self.right_img = QLabel()
        self.left_img.setPixmap(QPixmap("images/UI/up.jpeg"))
        self.right_img.setPixmap(QPixmap("images/UI/right.jpeg"))
        self.left_img.setAlignment(Qt.AlignCenter)
        self.right_img.setAlignment(Qt.AlignCenter)
        mid_img_layout.addWidget(self.left_img)
        mid_img_layout.addStretch(0)
        mid_img_layout.addWidget(self.right_img)
        mid_img_widget.setLayout(mid_img_layout)
        up_img_button = QPushButton("上传图片")
        det_img_button = QPushButton("开始检测")
        up_img_button.clicked.connect(self.upload_img)
        det_img_button.clicked.connect(self.detect_img)
        up_img_button.setFont(font_main)
        det_img_button.setFont(font_main)
        up_img_button.setStyleSheet("QPushButton{color:white}"
                                    "QPushButton:hover{background-color: rgb(2,110,180);}"
                                    "QPushButton{background-color:rgb(48,124,208)}"
                                    "QPushButton{border:2px}"
                                    "QPushButton{border-radius:5px}"
                                    "QPushButton{padding:5px 5px}"
                                    "QPushButton{margin:5px 5px}")
        det_img_button.setStyleSheet("QPushButton{color:white}"
                                     "QPushButton:hover{background-color: rgb(2,110,180);}"
                                     "QPushButton{background-color:rgb(48,124,208)}"
                                     "QPushButton{border:2px}"
                                     "QPushButton{border-radius:5px}"
                                     "QPushButton{padding:5px 5px}"
                                     "QPushButton{margin:5px 5px}")
        img_detection_layout.addWidget(img_detection_title, alignment=Qt.AlignCenter)
        img_detection_layout.addWidget(mid_img_widget, alignment=Qt.AlignCenter)
        img_detection_layout.addWidget(up_img_button)
        img_detection_layout.addWidget(det_img_button)
        img_detection_widget.setLayout(img_detection_layout)

        # todo 视频识别界面
        # 视频识别界面的逻辑比较简单，基本就从上到下的逻辑
        vid_detection_widget = QWidget()
        vid_detection_layout = QVBoxLayout()
        vid_title = QLabel("视频检测功能")
        vid_title.setFont(font_title)
        self.vid_img = QLabel()
        self.vid_img.setPixmap(QPixmap("images/UI/up.jpeg"))
        vid_title.setAlignment(Qt.AlignCenter)
        self.vid_img.setAlignment(Qt.AlignCenter)
        self.webcam_detection_btn = QPushButton("摄像头实时监测")
        self.mp4_detection_btn = QPushButton("视频文件检测")
        self.vid_stop_btn = QPushButton("停止检测")
        self.webcam_detection_btn.setFont(font_main)
        self.mp4_detection_btn.setFont(font_main)
        self.vid_stop_btn.setFont(font_main)
        self.webcam_detection_btn.setStyleSheet("QPushButton{color:white}"
                                                "QPushButton:hover{background-color: rgb(2,110,180);}"
                                                "QPushButton{background-color:rgb(48,124,208)}"
                                                "QPushButton{border:2px}"
                                                "QPushButton{border-radius:5px}"
                                                "QPushButton{padding:5px 5px}"
                                                "QPushButton{margin:5px 5px}")
        self.mp4_detection_btn.setStyleSheet("QPushButton{color:white}"
                                             "QPushButton:hover{background-color: rgb(2,110,180);}"
                                             "QPushButton{background-color:rgb(48,124,208)}"
                                             "QPushButton{border:2px}"
                                             "QPushButton{border-radius:5px}"
                                             "QPushButton{padding:5px 5px}"
                                             "QPushButton{margin:5px 5px}")
        self.vid_stop_btn.setStyleSheet("QPushButton{color:white}"
                                        "QPushButton:hover{background-color: rgb(2,110,180);}"
                                        "QPushButton{background-color:rgb(48,124,208)}"
                                        "QPushButton{border:2px}"
                                        "QPushButton{border-radius:5px}"
                                        "QPushButton{padding:5px 5px}"
                                        "QPushButton{margin:5px 5px}")
        self.webcam_detection_btn.clicked.connect(self.open_cam)
        self.mp4_detection_btn.clicked.connect(self.open_mp4)
        self.vid_stop_btn.clicked.connect(self.close_vid)
        # 添加组件到布局上
        vid_detection_layout.addWidget(vid_title)
        vid_detection_layout.addWidget(self.vid_img)
        vid_detection_layout.addWidget(self.webcam_detection_btn)
        vid_detection_layout.addWidget(self.mp4_detection_btn)
        vid_detection_layout.addWidget(self.vid_stop_btn)
        vid_detection_widget.setLayout(vid_detection_layout)

        # todo 关于界面
        about_widget = QWidget()
        about_layout = QVBoxLayout()
        about_title = QLabel('欢迎使用目标检测系统\n\n 本项目由戴威基于yolov5和Facenet封装而成\n仅供内部使用，不允许不授权而商业使用')  # todo 修改欢迎词语
        about_title.setFont(QFont('楷体', 18))
        about_title.setAlignment(Qt.AlignCenter)
        about_img = QLabel()
        about_img.setPixmap(QPixmap('images/UI/qq.png'))
        about_img.setAlignment(Qt.AlignCenter)

        # label4.setText("<a href='https://oi.wiki/wiki/学习率的调整'>如何调整学习率</a>")
        label_super = QLabel()  # todo
        label_super.setFont(QFont('楷体', 16))
        label_super.setOpenExternalLinks(True)
        # label_super.setOpenExternalLinks(True)
        label_super.setAlignment(Qt.AlignRight)
        about_layout.addWidget(about_title)
        about_layout.addStretch()
        about_layout.addWidget(about_img)
        about_layout.addStretch()
        about_layout.addWidget(label_super)
        about_widget.setLayout(about_layout)

        self.left_img.setAlignment(Qt.AlignCenter)
        self.addTab(img_detection_widget, '图片检测')
        self.addTab(vid_detection_widget, '视频检测')
        self.addTab(about_widget, '附加功能')
        self.setTabIcon(0, QIcon('images/UI/lufei.png'))
        self.setTabIcon(1, QIcon('images/UI/lufei.png'))
        self.setTabIcon(2, QIcon('images/UI/lufei.png'))

    '''
    ***上传图片***
    '''
    def upload_img(self):
        # 选择录像文件进行读取
        fileName, fileType = QFileDialog.getOpenFileName(self, 'Choose file', '', '*.jpg *.png *.tif *.jpeg')
        if fileName:
            suffix = fileName.split(".")[-1]
            # 上传图片功能页面的原始图片保存，将上传的原始图片保存为tmp_upload 将上传后的图片保存为upload_show_result 用于后面的人脸识别 不要多目标识别后的图片 由于识别框会导致精度降低
            save_path = osp.join("images/tmp", "tmp_upload." + suffix)
            shutil.copy(fileName, save_path)
            # 应该调整一下图片的大小，然后统一防在一起
            im0 = cv2.imread(save_path)
            resize_scale = self.output_size / im0.shape[0]
            im0 = cv2.resize(im0, (0, 0), fx=resize_scale, fy=resize_scale)
            cv2.imwrite("images/tmp/upload_show_result.jpg", im0)
            # self.right_img.setPixmap(QPixmap("images/tmp/single_result.jpg"))
            self.img2predict = fileName
            self.left_img.setPixmap(QPixmap("images/tmp/upload_show_result.jpg"))
            # todo 上传图片之后右侧的图片重置，
            self.right_img.setPixmap(QPixmap("images/UI/right.jpeg"))

    '''
    ***检测图片***
    '''
    def detect_img(self):
        model = self.model
        output_size = self.output_size
        source = self.img2predict  # file/dir/URL/glob, 0 for webcam
        imgsz = [640,640]  # inference size (pixels)
        conf_thres = 0.25  # confidence threshold
        iou_thres = 0.45  # NMS IOU threshold
        max_det = 1000  # maximum detections per image
        device = self.device  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        view_img = False  # show results
        save_txt = False  # save results to *.txt
        save_conf = False  # save confidences in --save-txt labels
        save_crop = False  # save cropped prediction boxes
        nosave = False  # do not save images/videos
        classes = None  # filter by class: --class 0, or --class 0 2 3
        agnostic_nms = False  # class-agnostic NMS
        augment = False  # ugmented inference
        visualize = False  # visualize features
        line_thickness = 3  # bounding box thickness (pixels)
        hide_labels = False  # hide labels
        hide_conf = False  # hide confidences
        half = False  # use FP16 half-precision inference
        dnn = False  # use OpenCV DNN for ONNX inference
        print(source)
        if source == "":
            QMessageBox.warning(self, "请上传", "请先上传图片再进行检测")
        else:
            source = str(source)
            device = select_device(self.device)
            webcam = False
            stride, names, pt, jit, onnx = model.stride, model.names, model.pt, model.jit, model.onnx
            imgsz = check_img_size(imgsz, s=stride)  # check image size
            save_img = not nosave and not source.endswith('.txt')  # save inference images
            # Dataloader
            if webcam:
                view_img = check_imshow()
                cudnn.benchmark = True  # set True to speed up constant image size inference
                dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt and not jit)
                bs = len(dataset)  # batch_size
            else:
                dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt and not jit)
                bs = 1  # batch_size
            vid_path, vid_writer = [None] * bs, [None] * bs
            # Run inference
            if pt and device.type != 'cpu':
                model(torch.zeros(1, 3, *imgsz).to(device).type_as(next(model.model.parameters())))  # warmup
            dt, seen = [0.0, 0.0, 0.0], 0
            for path, im, im0s, vid_cap, s in dataset:
                t1 = time_sync()
                im = torch.from_numpy(im).to(device)
                im = im.half() if half else im.float()  # uint8 to fp16/32
                im /= 255  # 0 - 255 to 0.0 - 1.0
                if len(im.shape) == 3:
                    im = im[None]  # expand for batch dim
                t2 = time_sync()
                dt[0] += t2 - t1
                # Inference
                # visualize = increment_path(save_dir / Path(path).stem, mkdir=True) if visualize else False
                pred = model(im, augment=augment, visualize=visualize)
                t3 = time_sync()
                dt[1] += t3 - t2
                # NMS
                pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
                dt[2] += time_sync() - t3
                # Second-stage classifier (optional)
                # pred = utils.general.apply_classifier(pred, classifier_model, im, im0s)
                # Process predictions
                for i, det in enumerate(pred):  # per image
                    # 更改默认加载的模型 在人脸识别层进行模型选择
                    recognize_result = Recognize(compre_face_base_url, api_key, "images/tmp/upload_show_result.jpg", 0,
                                                 "0.8", 1,
                                                 "landmarks", False)
                    Face_result = recognize_result
                    category = Dataset.find_category(Face_result, Dataset.categories)
                    print(category)
                    # 更改权重文件 用于检测验断电工作人员 和 验断电监管人员
                    if category == "外勤人员":
                        print("默认模型")
                    elif category == "验断电监管人员":
                        print("不是默认模型，正在更改")
                        self.model = self.model_load(
                            "D:/DL-ML-DRL/CV/yolo-series/yolov5-yolo412/yolov5_facenet/runs/train/exp7/weights/best.pt",
                            device=self.device)  # todo 指明模型加载的位置的设备
                        model = self.model
                    elif category == "验断电操作人员":
                        print("不是默认模型，正在更改")
                        self.model = self.model_load(
                            "D:/DL-ML-DRL/CV/yolo-series/yolov5-yolo412/yolov5_facenet/runs/train/exp7/weights/best.pt",
                            device=self.device)  # todo 指明模型加载的位置的设备
                        model = self.model
                    seen += 1
                    sdaiwei=""
                    snumber=""
                    if webcam:  # batch_size >= 1
                        p, im0, frame = path[i], im0s[i].copy(), dataset.count
                        s += f'{i}: '
                    else:
                        p, im0, frame = path, im0s.copy(), getattr(dataset, 'frame', 0)
                    p = Path(p)  # to Path
                    s += '%gx%g ' % im.shape[2:]  # print string
                    gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
                    imc = im0.copy() if save_crop else im0  # for save_crop
                    annotator = Annotator(im0, line_width=line_thickness, example=str(names))
                    if len(det):
                        # Rescale boxes from img_size to im0 size
                        det[:, :4] = scale_coords(im.shape[2:], det[:, :4], im0.shape).round()

                        # Print results
                        for c in det[:, -1].unique():
                            n = (det[:, -1] == c).sum()  # detections per class
                            # daiwei s之前的代码中使其实现了路径和图片大小的输出，这里是添加上识别结果，直接新建sdaiwei进行截取,我们不要之前的字符串，只要现在开始之后的
                            # s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string
                            sdaiwei += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                        # Write results
                        for *xyxy, conf, cls in reversed(det):
                            if save_txt:  # Write to file
                                xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(
                                    -1).tolist()  # normalized xywh
                                line = (cls, *xywh, conf) if save_conf else (cls, *xywh)  # label format
                                # with open(txt_path + '.txt', 'a') as f:
                                #     f.write(('%g ' * len(line)).rstrip() % line + '\n')

                            if save_img or save_crop or view_img:  # Add bbox to image
                                c = int(cls)  # integer class
                                label = None if hide_labels else (names[c] if hide_conf else f'{names[c]} {conf:.2f}')
                                annotator.box_label(xyxy, label, color=colors(c, True))
                                # if save_crop:
                                #     save_one_box(xyxy, imc, file=save_dir / 'crops' / names[c] / f'{p.stem}.jpg',
                                #                  BGR=True)
                    # 放置到保存当前处理图像的后面，否则人脸识别的是前一张
                    # # Print time (inference-only)
                    # # daiwei 修改输出日志
                    # # LOGGER.info(f'{s}Done. ({t3 - t2:.3f}s)')
                    # # 输出结果为：image 1/1 D:\DL-ML-DRL\CV\yolo-series\yolov5-yolo412\yolov5master\data\images\12.jpg: 640x480 1 head, 1 other_clothes, 1 wrist, 1 watch, Done. (0.059s)
                    # LOGGER.info(f'{sdaiwei}Done. ({t3 - t2:.3f}s)')
                    # # 输出结果为：1 head, 1 other_clothes, 1 wrist, 1 watch, Done. (0.059s)
                    # #daiwei 保存图片识别结果到txt
                    # content = f'{Face_result}\n{sdaiwei}\n'
                    # if "head" in content:
                    #     snumber += "1"
                    # if "helmet" in content or "helmets" in content:
                    #     snumber += "2"
                    # if "reflective_clothes" in content:
                    #     snumber += "3"
                    # if "other_clothes" in content:
                    #     snumber += "4"
                    # if "wrist" in content or "wrists" in content:
                    #     snumber += "5"
                    # if "watch" in content:
                    #     snumber += "6"
                    # snumber += "\n"
                    # with open("D:/DL-ML-DRL/CV/yolo-series/yolov5-yolo412/yolov5master/runs/result.txt", "a") as file:
                    #     file.write(content)
                    #
                    # with open("D:/DL-ML-DRL/CV/yolo-series/yolov5-yolo412/yolov5master/runs/resultnumber.txt", "a") as file:
                    #     file.write(snumber)
                    # Stream results
                    im0 = annotator.result()
                    # if view_img:
                    #     cv2.imshow(str(p), im0)
                    #     cv2.waitKey(1)  # 1 millisecond
                    # Save results (image with detections)
                    resize_scale = output_size / im0.shape[0]
                    im0 = cv2.resize(im0, (0, 0), fx=resize_scale, fy=resize_scale)
                    # single_result 为对图片进行多目标识别后
                    cv2.imwrite("images/tmp/single_result.jpg", im0)
                    # 目前的情况来看，应该只是ubuntu下会出问题，但是在windows下是完整的，所以继续
                    self.right_img.setPixmap(QPixmap("images/tmp/single_result.jpg"))

                    # 已经融合人脸识别,并加载了模型，现在在特征层进行模型加载
                    modelsfeature = Dataset.modelsfeature.get(category)
                    print(modelsfeature)
                    Nochange = Dataset.contains_all_items(f'{sdaiwei}', modelsfeature)
                    if Nochange == False:
                        print("特征不匹配，正在重新识别人脸，并重载模型")
                        while Nochange == False:
                            # 重新进行多目标识别操作
                            recognize_result = Recognize(compre_face_base_url, api_key, "images/tmp/upload_show_result.jpg",
                                                         0, "0.8", 1,
                                                         "landmarks", False)
                            Face_result = recognize_result
                            category = Dataset.find_category(Face_result, Dataset.categories)
                            if category == "外勤人员":
                                print("重识别后为外勤人员，加载对应模型")
                                self.model = self.model_load(
                                    "D:/DL-ML-DRL/CV/yolo-series/yolov5-yolo412/yolov5_facenet/runs/train/exp7/weights/best.pt",
                                    device=self.device)  # todo 指明模型加载的位置的设备
                                model = self.model
                            elif category == "验断电监管人员":
                                print("重识别后为验断电监管人员，加载对应模型")
                                self.model = self.model_load(
                                    "D:/DL-ML-DRL/CV/yolo-series/yolov5-yolo412/yolov5_facenet/runs/train/exp7/weights/best.pt",
                                    device=self.device)  # todo 指明模型加载的位置的设备
                                model = self.model

                            elif category == "验断电操作人员":
                                print("重识别后为验断电操作人员，加载对应模型")
                                self.model = self.model_load(
                                    "D:/DL-ML-DRL/CV/yolo-series/yolov5-yolo412/yolov5_facenet/runs/train/exp7/weights/best.pt",
                                    device=self.device)  # todo 指明模型加载的位置的设备
                                model = self.model

                            modelsfeature = Dataset.modelsfeature.get(category)
                            Nochange = Dataset.contains_all_items(f'{sdaiwei}', modelsfeature)
                    else:
                        print("特征完全匹配")
                    # Print time (inference-only)
                    # daiwei 修改输出日志
                    # LOGGER.info(f'{s}Done. ({t3 - t2:.3f}s)')
                    # 输出结果为：image 1/1 D:\DL-ML-DRL\CV\yolo-series\yolov5-yolo412\yolov5master\data\images\12.jpg: 640x480 1 head, 1 other_clothes, 1 wrist, 1 watch, Done. (0.059s)
                    LOGGER.info(f'{sdaiwei}Done. ({t3 - t2:.3f}s)')
                    # # 输出结果为：1 head, 1 other_clothes, 1 wrist, 1 watch, Done. (0.059s)
                    # #daiwei 保存图片识别结果到txt
                    # content = f'{Face_result}\n{sdaiwei}\n'
                    # if "head" in content:
                    #     snumber += "1"
                    # if "helmet" in content or "helmets" in content:
                    #     snumber += "2"
                    # if "reflective_clothes" in content:
                    #     snumber += "3"
                    # if "other_clothes" in content:
                    #     snumber += "4"
                    # if "watch" in content:
                    #     snumber += "5"
                    # snumber += "\n"
                    # with open("D:/DL-ML-DRL/CV/yolo-series/yolov5-yolo412/yolov5master/runs/result.txt", "a") as file:
                    #     file.write(content)
                    #
                    # with open("D:/DL-ML-DRL/CV/yolo-series/yolov5-yolo412/yolov5master/runs/resultnumber.txt", "a") as file:
                    #     file.write(snumber)
    # 视频检测，逻辑基本一致，有两个功能，分别是检测摄像头的功能和检测视频文件的功能，先做检测摄像头的功能。

    '''
    ### 界面关闭事件 ### 
    '''
    def closeEvent(self, event):
        reply = QMessageBox.question(self,
                                     'quit',
                                     "Are you sure?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
            event.accept()
        else:
            event.ignore()

    '''
    ### 视频关闭事件 ### 
    '''

    def open_cam(self):
        self.webcam_detection_btn.setEnabled(False)
        self.mp4_detection_btn.setEnabled(False)
        self.vid_stop_btn.setEnabled(True)
        self.vid_source = '0'
        self.webcam = True
        # 把按钮给他重置了
        # print("GOGOGO")
        th = threading.Thread(target=self.detect_vid)
        th.start()

    '''
    ### 开启视频文件检测事件 ### 
    '''

    def open_mp4(self):
        fileName, fileType = QFileDialog.getOpenFileName(self, 'Choose file', '', '*.mp4 *.avi')
        if fileName:
            self.webcam_detection_btn.setEnabled(False)
            self.mp4_detection_btn.setEnabled(False)
            # self.vid_stop_btn.setEnabled(True)
            self.vid_source = fileName
            self.webcam = False
            th = threading.Thread(target=self.detect_vid)
            th.start()

    '''
    ### 视频开启事件 ### 
    '''

    # 视频和摄像头的主函数是一样的，不过是传入的source不同罢了
    def detect_vid(self):
        keep = ""
        # 全局变量keep
        # pass
        model = self.model
        output_size = self.output_size
        # source = self.img2predict  # file/dir/URL/glob, 0 for webcam
        imgsz = [640, 640]  # inference size (pixels)
        conf_thres = 0.25  # confidence threshold
        iou_thres = 0.45  # NMS IOU threshold
        max_det = 1000  # maximum detections per image
        # device = self.device  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        view_img = False  # show results
        save_txt = False  # save results to *.txt
        save_conf = False  # save confidences in --save-txt labels
        save_crop = False  # save cropped prediction boxes
        nosave = False  # do not save images/videos
        classes = None  # filter by class: --class 0, or --class 0 2 3
        agnostic_nms = False  # class-agnostic NMS
        augment = False  # ugmented inference
        visualize = False  # visualize features
        line_thickness = 3  # bounding box thickness (pixels)
        hide_labels = False  # hide labels
        hide_conf = False  # hide confidences
        half = False  # use FP16 half-precision inference
        dnn = False  # use OpenCV DNN for ONNX inference
        source = str(self.vid_source)
        webcam = self.webcam
        device = select_device(self.device)
        stride, names, pt, jit, onnx = model.stride, model.names, model.pt, model.jit, model.onnx
        imgsz = check_img_size(imgsz, s=stride)  # check image size
        save_img = not nosave and not source.endswith('.txt')  # save inference images
        capture_interval = 0.005 # 捕获间隔设置秒数 #daiwei 抓帧
        # 亲测0.05可行，非常流程，同时能一直保持人脸在线，同理0.01更是
        # 亲测1可行，但是停顿，也能一直保持人脸在线，同理3
        last_capture_time = time.time()  # 初始化上次捕获时间 #daiwei 抓帧
        # Dataloader
        if webcam:
            view_img = check_imshow()
            cudnn.benchmark = True  # set True to speed up constant image size inference
            dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt and not jit)
            bs = len(dataset)  # batch_size
        else:
            dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt and not jit)
            bs = 1  # batch_size
        vid_path, vid_writer = [None] * bs, [None] * bs
        # Run inference
        if pt and device.type != 'cpu':
            model(torch.zeros(1, 3, *imgsz).to(device).type_as(next(model.model.parameters())))  # warmup
        dt, seen = [0.0, 0.0, 0.0], 0
        for path, im, im0s, vid_cap, s in dataset:
            current_time = time.time() #daiwei 抓帧
            if current_time - last_capture_time < capture_interval: #daiwei 抓帧
                continue  # 如果没有达到1秒，则跳过此帧 #daiwei 抓帧
            # 下面是处理每一帧的代码...
            last_capture_time = current_time  # 更新上次捕获时间  #daiwei 抓帧
            t1 = time_sync()
            im = torch.from_numpy(im).to(device)
            im = im.half() if half else im.float()  # uint8 to fp16/32
            im /= 255  # 0 - 255 to 0.0 - 1.0
            if len(im.shape) == 3:
                im = im[None]  # expand for batch dim
            t2 = time_sync()
            dt[0] += t2 - t1
            # Inference
            # visualize = increment_path(save_dir / Path(path).stem, mkdir=True) if visualize else False
            pred = model(im, augment=augment, visualize=visualize)
            t3 = time_sync()
            dt[1] += t3 - t2
            # NMS
            pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
            dt[2] += time_sync() - t3
            # Second-stage classifier (optional)
            # pred = utils.general.apply_classifier(pred, classifier_model, im, im0s)
            # Process predictions
            for i, det in enumerate(pred):  # per image

                sdaiwei = ""
                snumber = ""

                seen += 1
                if webcam:  # batch_size >= 1
                    p, im0, frame = path[i], im0s[i].copy(), dataset.count
                    s += f'{i}: '
                else:
                    p, im0, frame = path, im0s.copy(), getattr(dataset, 'frame', 0)
                p = Path(p)  # to Path
                # save_path = str(save_dir / p.name)  # im.jpg
                # txt_path = str(save_dir / 'labels' / p.stem) + (
                #     '' if dataset.mode == 'image' else f'_{frame}')  # im.txt
                s += '%gx%g ' % im.shape[2:]  # print string
                gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
                imc = im0.copy() if save_crop else im0  # for save_crop
                # 上传的视频切帧后的图像 命名为single_vid 用于后面的人脸识别 不要多目标识别后的图片 由于识别框会导致精度降低
                cv2.imwrite("images/tmp/single_vid.jpg", im0)
                annotator = Annotator(im0, line_width=line_thickness, example=str(names))
                if len(det):
                    # Rescale boxes from img_size to im0 size
                    det[:, :4] = scale_coords(im.shape[2:], det[:, :4], im0.shape).round()

                    # Print results
                    for c in det[:, -1].unique():
                        n = (det[:, -1] == c).sum()  # detections per class
                        # daiwei s之前的代码中使其实现了路径和图片大小的输出，这里是添加上识别结果，直接新建sdaiwei进行截取,我们不要之前的字符串，只要现在开始之后的
                        # s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string
                        sdaiwei += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string


                    # Write results
                    for *xyxy, conf, cls in reversed(det):
                        if save_txt:  # Write to file
                            xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(
                                -1).tolist()  # normalized xywh
                            line = (cls, *xywh, conf) if save_conf else (cls, *xywh)  # label format
                            # with open("D:/DL-ML-DRL/CV/yolo-series/yolov5-yolo412/yolov5master/runs/result" + '.txt', 'a') as f:
                            #     f.write(('%g ' * len(line)).rstrip() % line + '\n')

                        if save_img or save_crop or view_img:  # Add bbox to image
                            c = int(cls)  # integer class
                            label = None if hide_labels else (names[c] if hide_conf else f'{names[c]} {conf:.2f}')
                            annotator.box_label(xyxy, label, color=colors(c, True))
                            # if save_crop:
                            #     save_one_box(xyxy, imc, file=save_dir / 'crops' / names[c] / f'{p.stem}.jpg',
                            #                  BGR=True)
                # 放置到保存当前处理图像的后面，否则人脸识别的是前一张
                # # Print time (inference-only)
                # # daiwei 修改输出日志
                # # LOGGER.info(f'{s}Done. ({t3 - t2:.3f}s)')
                # # 输出结果为：image 1/1 D:\DL-ML-DRL\CV\yolo-series\yolov5-yolo412\yolov5master\data\images\12.jpg: 640x480 1 head, 1 other_clothes, 1 wrist, 1 watch, Done. (0.059s)
                # LOGGER.info(f'{sdaiwei}Done. ({t3 - t2:.3f}s)')
                # # 输出结果为：1 head, 1 other_clothes, 1 wrist, 1 watch, Done. (0.059s)
                # # daiwei 保存图片识别结果到txt
                # if keep == Face_result:
                #     Face_result = ""
                # else:
                #     keep = Face_result
                # content = f'{Face_result}\n{sdaiwei}\n'
                # if "head" in content:
                #     snumber += "1"
                # if "helmet" in content or "helmets" in content:
                #     snumber += "2"
                # if "reflective_clothes" in content:
                #     snumber += "3"
                # if "other_clothes" in content:
                #     snumber += "4"
                # if "wrist" in content or "wrists" in content:
                #     snumber += "5"
                # if "watch" in content:
                #     snumber += "6"
                # snumber += "\n"
                # with open("D:/DL-ML-DRL/CV/yolo-series/yolov5-yolo412/yolov5master/runs/result.txt", "a") as file:
                #     file.write(content)
                #
                # with open("D:/DL-ML-DRL/CV/yolo-series/yolov5-yolo412/yolov5master/runs/resultnumber.txt", "a") as file:
                #     file.write(snumber)

                # Stream results
                # Save results (image with detections)
                im0 = annotator.result()
                frame = im0
                resize_scale = output_size / frame.shape[0]
                frame_resized = cv2.resize(frame, (0, 0), fx=resize_scale, fy=resize_scale)
                cv2.imwrite("images/tmp/single_result_vid.jpg", frame_resized) #上传图片后，识别后的图片保存路径
                self.vid_img.setPixmap(QPixmap("images/tmp/single_result_vid.jpg"))
                #实时视频开启后，识别后的最后一帧图片保存路径  ！！！这里需要更正，并不是最后一帧，而是每一帧，这里不过进行了覆盖，倘若要获取每一帧，遍历名称即可
                # self.vid_img
                # if view_img:
                # cv2.imshow(str(p), im0)
                # self.vid_img.setPixmap(QPixmap("images/tmp/single_result_vid.jpg"))
                # cv2.waitKey(1)  # 1 millisecond

                recognize_result = Recognize(compre_face_base_url, api_key, "images/tmp/single_vid.jpg", 0,
                                             "0.8", 1, "landmarks", False)
                Face_result=recognize_result
                # Print time (inference-only)
                # daiwei 修改输出日志
                # LOGGER.info(f'{s}Done. ({t3 - t2:.3f}s)')
                # 输出结果为：image 1/1 D:\DL-ML-DRL\CV\yolo-series\yolov5-yolo412\yolov5master\data\images\12.jpg: 640x480 1 head, 1 other_clothes, 1 wrist, 1 watch, Done. (0.059s)
                LOGGER.info(f'{sdaiwei}Done. ({t3 - t2:.3f}s)')
                # 输出结果为：1 head, 1 other_clothes, 1 wrist, 1 watch, Done. (0.059s)
                # daiwei 保存图片识别结果到txt
                if keep == Face_result:
                    Face_result = ""
                else:
                    keep = Face_result
                content = f'{Face_result}\n{sdaiwei}\n'
                if "head" in content:
                    snumber += "1"
                if "helmet" in content or "helmets" in content:
                    snumber += "2"
                if "reflective_clothes" in content:
                    snumber += "3"
                if "other_clothes" in content:
                    snumber += "4"
                if "wrist" in content or "wrists" in content:
                    snumber += "5"
                if "watch" in content:
                    snumber += "6"
                snumber += "\n"
                with open("D:/DL-ML-DRL/CV/yolo-series/yolov5-yolo412/yolov5master/runs/result.txt", "a") as file:
                    file.write(content)

                with open("D:/DL-ML-DRL/CV/yolo-series/yolov5-yolo412/yolov5master/runs/resultnumber.txt", "a") as file:
                    file.write(snumber)
            if cv2.waitKey(25) & self.stopEvent.is_set() == True:
                self.stopEvent.clear()
                self.webcam_detection_btn.setEnabled(True)
                self.mp4_detection_btn.setEnabled(True)
                self.reset_vid()
                break
        # self.reset_vid()

    '''
    ### 界面重置事件 ### 
    '''

    def reset_vid(self):
        self.webcam_detection_btn.setEnabled(True)
        self.mp4_detection_btn.setEnabled(True)
        self.vid_img.setPixmap(QPixmap("images/UI/up.jpeg"))
        self.vid_source = '0'
        self.webcam = True

    '''
    ### 视频重置事件 ### 
    '''

    def close_vid(self):
        self.stopEvent.set()
        self.reset_vid()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
