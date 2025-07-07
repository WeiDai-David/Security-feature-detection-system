# Author : 戴威 Wei Dai
# Authority :
# This project involves commercial use and patented inventions, and cannot be reproduced.
# It requires permission from the copyright owner, Wei Dai, and contact information, 944899059@qq.com
# 项目基于yolov5和Facenet实现，尽管这两个模型开源，但是整个项目的各种封装以及应用实际落地过程中所需要的源码全部由本人编写，目前处于项目保护阶段，不允许未授权使用

import requests

# CompreFace API地址和API密钥
compre_face_base_url = 'http://localhost:8000'  # CompreFace实例的URL
api_key = '7d076e33-ae5d-4301-bc31-db8649e74bd6'  # API密钥 针对示例项目的api

# 创建subjects
def CreateSubject(compre_face_base_url,api_key,subject_name):
    # 设置请求的URL和headers
    post_url = f"{compre_face_base_url}/api/v1/recognition/subjects"
    post_headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }

    # # 要添加的主题名称
    # subject_name = 'SubjectTest'  # 替换为实际的主题名称
    # 通过传参的方式进来

    # 发送POST请求
    post_response = requests.post(post_url, headers=post_headers, json={'subject': subject_name})

    # 检查响应状态并打印结果
    if post_response.status_code == 200:
        print("主题添加成功:", post_response.json())
    # 显示主题添加失败，状态码201，但是201本身的意思表示“Created”。在HTTP协议中，这个状态码表示请求已成功，并且服务器创建了一个新的资源。它通常在完成POST请求后返回，指示服务器成功创建了客户端请求的资源。
    else:
        # print("主题添加失败，状态码:", post_response.status_code)
        print("主题添加成功")
# CreateSubject(compre_face_base_url,api_key,"SubjectTest")

# 获取所有subjects
def GetSubject(compre_face_base_url,api_key):
    # 设置请求的URL和headers
    get_url = f"{compre_face_base_url}/api/v1/recognition/subjects"  # 假设这是获取主题列表的端点
    get_headers = {
        'x-api-key': api_key
    }
    # 获取subjects
    # 发送GET请求
    get_response = requests.get(get_url, headers=get_headers)

    # 检查响应状态并打印结果
    if get_response.status_code == 200:
        print("获取数据成功:", get_response.json())
    else:
        print("获取数据失败，状态码:", get_response.status_code)
# GetSubject(compre_face_base_url,api_key)

# 重命名指定subjects
def Rename(compre_face_base_url,api_key,subject_name,new_subject_name):

    # 设置请求的URL
    url = f"{compre_face_base_url}/api/v1/recognition/subjects/{subject_name}"

    # 设置请求头部和数据
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }
    data = {
        'subject': new_subject_name
    }

    # 发起PUT请求
    response = requests.put(url, headers=headers, json=data)

    # 检查响应
    if response.status_code == 200:
        print('Subject renamed successfully:', response.json())
    else:
        print('Failed to rename subject. Status code:', response.status_code, 'Response:', response.text)
# Rename(compre_face_base_url,api_key,"SubjectTest","RenameSubjectTest")

# 删除subjects-使用subject名进行索引
def DeleteSubject(compre_face_base_url,api_key,subject_name):
    # 设置请求的URL
    url = f"{compre_face_base_url}/api/v1/recognition/subjects/{subject_name}"

    # 设置请求头部
    headers = {
        'x-api-key': api_key
    }

    # 发起DELETE请求
    response = requests.delete(url, headers=headers)

    # 检查响应
    if response.status_code == 200:
        print('Subject删除成功:', response.json())
    else:
        print('Subject删除失败。状态码:', response.status_code, '响应内容:', response.text)
# DeleteSubject(compre_face_base_url,api_key,"SubjectTest")

# 上传图片到subjects中-上传图片的时候可以获取到image_id
def UploadPicture(compre_face_base_url,api_key,subject_name,file_path):
    # 设置请求的URL
    url = f"{compre_face_base_url}/api/v1/recognition/faces?subject={subject_name}"

    # 设置请求头部
    headers = {
        'x-api-key': api_key
    }

    files = {
        'file': open(file_path, 'rb')  # 打开文件用于上传
    }

    response = requests.post(url, headers=headers, files=files)

    if response.status_code == 201:
        print('示例图片添加成功:', response.json())
    else:
        print('示例图片添加失败。状态码:', response.status_code, '响应内容:', response.text)
# UploadPicture(compre_face_base_url,api_key,"SubjectTest","D:/DL-ML-DRL/CV/FaceIdentify/compreface/FaceData/recognition/FaceTrain/奥特曼1.jpg")

# 获取某个subjects所有上传的图片
def GetPicture(compre_face_base_url,api_key,subject_name):

    # 设置查询参数（可选）
    params = {
        'page': 1,  # 页码
        'size': 10,  # 每页大小
        'subject': subject_name  # 主题名称
    }

    # 设置请求的URL和头部
    url = f"{compre_face_base_url}/api/v1/recognition/faces"
    headers = {
        'x-api-key': api_key
    }

    # 发起GET请求
    response = requests.get(url, headers=headers, params=params)

    # 检查响应
    if response.status_code == 200:
        print('获取列表成功:', response.json())
    else:
        print('获取列表失败。状态码:', response.status_code, '响应内容:', response.text)
# GetPicture(compre_face_base_url,api_key,"戴威")

# 删除指定subject的所有图片（可以通过指定图片id删除部分图片，但是本身一个subject只有几张图片，所以直接全删重新上传即可）
def DeleteSubjectPicture(compre_face_base_url,api_key,subject_name):
    url = f"{compre_face_base_url}/api/v1/recognition/faces?subject={subject_name}"
    headers = {
        'x-api-key': api_key
    }

    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        print('删除示例图片成功:', response.json())
    else:
        print('删除示例图片失败。状态码:', response.status_code, '响应内容:', response.text)
# DeleteSubjectPicture(compre_face_base_url,api_key,"戴威")

# Recognize人脸识别 (目前只开发人脸识别，后续根据库规模扩大，可以增加人脸验证进行双重检验)
def Recognize(compre_face_base_url,api_key,file_path,limit,det_prob_threshold,prediction_count,face_plugins,status):
    # 准备请求参数
    url = f"{compre_face_base_url}/api/v1/recognition/recognize"
    headers = {
        'x-api-key': api_key
    }
    files = {'file': open(file_path, 'rb')}
    data = {
        'limit': limit,  # 可选参数-识别人脸数量限制
        'det_prob_threshold': det_prob_threshold,  # 可选参数-检测人脸的置信度阈值
        'prediction_count': prediction_count,  # 可选参数-返回的最相似面部的数量
        'face_plugins': face_plugins,  # 可选参数-使用的插件
        'status': status  # 可选参数-状态
    }

    # 发送POST请求
    response = requests.post(url, headers=headers, files=files, data=data)

    # 输出结果
    if response.status_code == 200:
        result = response.json()
        subject_value = result['result'][0]['subjects'][0]['subject']
        probability = result['result'][0]['subjects'][0]['similarity']
        if probability > 0.5 :
            print('面部识别成功:', response.json(),"/n")
            print(subject_value)  # 从json中单独获取识别结果
            recognize_result = subject_value
            return recognize_result
        else:
            print("面部识别置信度过低，该人脸不在人脸识别库")
            recognize_result = "该人脸不在人脸识别库"
            return recognize_result
    else:
        print('面部识别失败，状态码:', response.status_code, '响应内容:', response.text)
        recognize_result = "该人脸不在人脸识别库"
        print(recognize_result)
        return recognize_result
# Recognize(compre_face_base_url,api_key,"D:/DL-ML-DRL/CV/FaceIdentify/compreface/FaceData/recognition/FaceTest/奥特曼Test1.jpeg",0,"0.8",1,"landmarks",False)

# 快捷操作
# 创建subjects # 获取所有subjects # 重命名指定subjects # 删除subjects-使用subject名进行索引 # 上传图片到subjects中
# 获取某个subjects所有上传的图片 # 删除指定subject的所有图片（可以通过指定图片id删除部分图片，但是本身一个subject只有几张图片，所以直接全删重新上传即可） # Recognize人脸识别
# CreateSubject(compre_face_base_url,api_key,"SubjectTest1")
# CreateSubject(compre_face_base_url,api_key,"SubjectTest2")
# GetSubject(compre_face_base_url,api_key)
# Rename(compre_face_base_url,api_key,"SubjectTest1","RenameSubjectTest1")
# Rename(compre_face_base_url,api_key,"SubjectTest2","RenameSubjectTest2")
# DeleteSubject(compre_face_base_url,api_key,"SubjectTest")
# UploadPicture(compre_face_base_url,api_key,"SubjectTest1","D:/DL-ML-DRL/CV/FaceIdentify/compreface/FaceData/recognition/FaceTrain/奥特曼1.jpg")
# UploadPicture(compre_face_base_url,api_key,"SubjectTest1","D:/DL-ML-DRL/CV/FaceIdentify/compreface/FaceData/recognition/FaceTrain/奥特曼2.jpeg")
# GetPicture(compre_face_base_url,api_key,"SubjectTest1")
# DeleteSubjectPicture(compre_face_base_url,api_key,"戴威")
# Recognize(compre_face_base_url,api_key,"D:/DL-ML-DRL/CV/FaceIdentify/compreface/FaceData/recognition/FaceTest/奥特曼Test1.jpeg",0,"0.8",1,"landmarks",False)

# 演示顺序
# DeleteSubject(compre_face_base_url,api_key,"戴威")
# DeleteSubject(compre_face_base_url,api_key,"SubjectTest2")
# CreateSubject(compre_face_base_url,api_key,"SubjectTest1")
# CreateSubject(compre_face_base_url,api_key,"米峰良")
# CreateSubject(compre_face_base_url,api_key,"周鲲鹏")
# GetSubject(compre_face_base_url,api_key)
# UploadPicture(compre_face_base_url,api_key,"米峰良","D:/DL-ML-DRL/CV/FaceIdentify/compreface/FaceData/recognition/FaceTrain/米峰良.jpg")
# UploadPicture(compre_face_base_url,api_key,"周鲲鹏","D:/DL-ML-DRL/CV/FaceIdentify/compreface/FaceData/recognition/FaceTrain/周鲲鹏.jpg")
# UploadPicture(compre_face_base_url,api_key,"SubjectTest1","D:/DL-ML-DRL/CV/FaceIdentify/compreface/FaceData/recognition/FaceTrain/奥特曼2.jpeg")
# GetPicture(compre_face_base_url,api_key,"SubjectTest1")
# recognize_result = Recognize(compre_face_base_url,api_key,"D:/DL-ML-DRL/CV/FaceIdentify/compreface/FaceData/recognition/FaceTest/奥特曼Test1.jpeg",0,"0.8",1,"landmarks",False)

# UploadPicture(compre_face_base_url,api_key,"SubjectTest2","D:/DL-ML-DRL/CV/FaceIdentify/compreface/FaceData/recognition/FaceTrain/马斯克1.jpg")
# UploadPicture(compre_face_base_url,api_key,"SubjectTest2","D:/DL-ML-DRL/CV/FaceIdentify/compreface/FaceData/recognition/FaceTrain/马斯克2.jpg")
# recognize_result = Recognize(compre_face_base_url,api_key,"D:/DL-ML-DRL/CV/FaceIdentify/compreface/FaceData/recognition/FaceTest/马斯克Test1.jpg",0,"0.8",1,"landmarks",False)
# 实时视频抓帧进行人脸识别
# recognize_result = Recognize(compre_face_base_url,api_key,"images/tmp/single_result_vid.jpg",0,"0.8",1,"landmarks",False)