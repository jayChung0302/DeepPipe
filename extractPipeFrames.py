import pandas as pd
import cv2
import os
from datetime import time
import glob
from tqdm import tqdm
import numpy as np

def video2frame(videofilename, save_path):
    """This function is to make video's frame to the images"""
    vidcap = cv2.VideoCapture(videofilename)
    count = 0
    length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    print('total_frames:{}, time:{}, width:{}, height:{}, fps:{}'.format(length, length / fps, width, height, fps))
    while True:
        success, img = vidcap.read()
        if not success:
            break
        fname = "{}{}.jpg".format("frame", "{0:06d}".format(count))
        #         gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(save_path + fname, img)  # save frame as JPEG file
        count += 1
    print("{} images are extracted in {}.".format(count, save_path))

def INDEX_video2frame(videofilename, save_path, time):
    """This function is to make video's frame to the images from index time"""
    vidcap = cv2.VideoCapture(videofilename)
    count = 0
    frame_count = 0
    length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    index_frame = time * fps  # (number of frames) = time * fps
    print('total_frames:{}, time:{}, width:{}, height:{}, fps:{}'.format(length, length / fps, width, height, fps))
    while True:
        success, img = vidcap.read()
        frame_count = frame_count + 1
        if frame_count < index_frame - 10:
            continue
        if frame_count > index_frame + 10:
            break
        if not success:
            break
        fname = "{}.jpg".format("{0:06d}".format(count))
        #gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        try:
            if not (os.path.isdir(save_path)):
                os.makedirs(save_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                print("Failed to create directory.")
                raise
        cv2.imwrite(save_path + '/' + fname, img)  # save frame as JPEG file
        count += 1
    print("{} images are extracted in {}.".format(count, save_path))

if __name__ == '__main__':
    excel_name = 'C:/Users/lenovo/Dropbox/PROJECT/Sewer Pipe/location_information/관로 이상항목별 동영상 재생위치 - 김포.xlsx'
    df = pd.read_excel(excel_name, sheet_name=0)
    cctv_name = list(df['Unnamed: 1'])
    defect_name = list(df['Unnamed: 2'])
    defect_time = list(df['Unnamed: 3'])
    defect_dic = {}

    save_path = 'C:/Users/lenovo/Dropbox/LAB/DATASET/Datasets_SewerPipe'
    fpath = 'E:/00.성과물/김포 동영상/기본계획/'  # 추출할 비디오 데이터 폴더들이 들어있는 main directory 설정.
    ext = '.AVI'

    for i, k in enumerate(zip(cctv_name, defect_name, defect_time)):
        cctv_name, defect_name, defect_time = k
        print(cctv_name, defect_name, defect_time)
        if i == 0:
            continue
        if defect_name not in defect_dic:
            defect_dic[defect_name] = 1
        else :
            defect_dic[defect_name] = defect_dic[defect_name] + 1

        defect_time = defect_time.replace('[','').replace(']','').split(':')
        defect_time = time(int(defect_time[0]), int(defect_time[1]), int(defect_time[2])).second

        INDEX_video2frame(fpath + cctv_name + ext, save_path + '/' + defect_name, defect_time)
        break
    class_names = sorted(list(defect_dic.keys()))
