#-*- coding: utf-8 -*-
import torch
import torch.nn as nn
import torchvision
import torchvision.models as models
import torchvision.transforms as transforms
import os
import pickle
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
from tkinter import *
from tkinter import filedialog
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image


torch.nn.Module.dump_patches = True

root = Tk()
root.title('DeepPipe - defect detection program')
root.geometry('740x630')

# information
def info():
    msgbox.showinfo("information", 'DeepPipe\nversion 0.0.1\nmade by Chung\nwhtnek@gmail.com\nNASSTECH E&C Co.')

# 파일 추가
def add_file():
    files = filedialog.askopenfilenames(title='Select image files', \
        filetypes=(('png file', "*.png"),('jpg file', '*.jpg'),\
             ("All files", "*.*")),\
            initialdir="/Users/")
    # 사용자가 선택한 파일 목록
    for file in files:
        list_file.insert(END, file)
    
# 선택 삭제
def del_file():
    for index in reversed(list_file.curselection()):
        list_file.delete(index)
        result_file.delete(index)
    

# 저장 경로 (폴더)
def browse_dest_path():
    folder_selected = filedialog.askdirectory(initialdir='/Users')
    if not folder_selected: # 사용자가 취소를 눌렀을 때
        return
    txt_dest_path.delete(0, END)
    txt_dest_path.insert(0, folder_selected)
    # print(txt_dest_path.get())

def check_valid_img(img, idx):
    if img.mode not in ["RGB", "LAB", "YCbCr", "HSV"]:
        msgbox.showerror('Channel dimension error', f'Use 3-dimensional RGB image. \
            {idx+1}-th image is not fitted with our network.')
        print(img.mode)
        return False
    else:
        return True

def get_result(idx, probs, preds, dic):
    statement = f'{idx} - top5:'
    for prob, pred in zip(probs, preds):
        statement += f'[{dic[pred.item()]} / {prob.item() * 100:.2f}%]'
    if cmb_save.get() == 'True':
        logfile = txt_dest_path.get()+'/log.txt'
        if os.path.exists(f'{logfile}'):
            option = 'a'
        else:
            option = 'w'
        f = open(logfile, option)
        f.write(statement+'\n')
        f.close()
    result_file.insert(END, statement)
    

def get_CAM(idx, net, img, preds):
    target_layer = net.layer4[-1]
    cam = GradCAM(model=net, target_layer=target_layer, use_cuda=False)
    target_category = preds[0].item()
    grayscale_cam = cam(input_tensor=img.unsqueeze(0), target_category=target_category)
    grayscale_cam = grayscale_cam[0, :]
    x = img.numpy()
    x = np.transpose(x, (1,2,0))
    visualization = show_cam_on_image(x, grayscale_cam)
    plt.imsave(f'{txt_dest_path.get()}/{idx}_activated_on_{target_category}.jpg',visualization)

def run_process(images):
    with open("class_names.pkl", "rb") as file:
        dic = pickle.load(file)
    use_gpu = True if cmb_gpu.get()=="True" else False
    if use_gpu:
        if not torch.cuda.is_available():
            msgbox.showwarning('GPU warning', 'CUDA is not available.\nSelect False instead.')
            return
        else:
            device = torch.device('cuda')
    else:
        device = torch.device('cpu')
    net = torch.load('resnet50.pth', map_location=device).eval()
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

    #TODO: 코드 효율 개선
    
    transform = transforms.Compose([
        transforms.Resize(224),
        transforms.ToTensor(),
        normalize
    ])
    to_tensor = transforms.ToTensor()
    trans_images = [transform(x) for x in images]
    
    soft = nn.Softmax()
    for idx, img in enumerate(trans_images):
        with torch.no_grad():
            if use_gpu:
                img = img.cuda()
            
            output = soft(net(img.unsqueeze(0))[0])
            probs, preds = torch.topk(output, 5)
            get_result(idx, probs, preds, dic)
        if cmb_CAM.get() == 'True':
            get_CAM(idx, net, to_tensor(images[idx]), preds)

        progress = (idx + 1) / len(trans_images) * 100
        p_var.set(progress)
        progress_bar.update()
        result_file.update()
    
    msgbox.showinfo("Info", "process is done")
    return

# 시작
def start():
    # 파일목록 확인
    if list_file.size() == 0:
        msgbox.showwarning("Warning", "Add image files")
        return
    images = []
    for idx, img_dir in enumerate(list_file.get(0,END)):
        img = Image.open(img_dir)
        if not check_valid_img(img, idx):
            return
        else:
            images.append(img)
    
    # classification
    run_process(images)

menu = Menu(root)

menu_file = Menu(menu, tearoff=0)
menu_file.add_command(label="info", command=info)
menu_file.add_separator()
menu_file.add_command(label="quit", command=root.quit)
menu.add_cascade(label="Menu", menu=menu_file)

# 파일 프레임(파일 추가, 선택 삭제)
file_frame = Frame(root)
file_frame.pack(fill="x", padx=5, pady=5)

btn_add_file = Button(file_frame, padx=5, pady=5, width=12, text="Add files", command=add_file)
btn_add_file.pack(side='left')

btn_delete_file = Button(file_frame, padx=5, pady=5, width=12, text="Delete files", command=del_file)
btn_delete_file.pack(side='left')

# 리스트 프레임
list_frame = Frame(root)
list_frame.pack(fill="both", padx=5, pady=5)

scrollbar = Scrollbar(list_frame)
scrollbar.pack(side='left', fill='y')

list_file = Listbox(list_frame, selectmode='extended', height=15, yscrollcommand=scrollbar.set)
list_file.pack(side='left',anchor='w', fill='both', expand=True)
scrollbar.config(command=list_file.yview)

# 결과 프레임
result_frame = Frame(root)
result_frame.pack(fill="both", padx=5, pady=5)


result_file = Listbox(list_frame, selectmode='extended', height=15, yscrollcommand=scrollbar.set)
result_file.pack(side='right', anchor='w', fill='both', expand=True)

# 저장경로 프레임
path_frame = LabelFrame(root, text="Save path")
path_frame.pack(fill='x', padx=5, pady=5)
txt_dest_path = Entry(path_frame)
txt_dest_path.pack(side="left", fill="x", expand=True, padx=5, pady=5, ipady=4) # ipad: 높이 변경

btn_dest_path = Button(path_frame, text="Search", width=10, command=browse_dest_path)
btn_dest_path.pack(side="right", padx=5, pady=5, ipady=5)

# 옵션 프레임
frame_option = LabelFrame(root, text="options")
frame_option.pack(fill='x', padx=5, pady=5, ipady=5)

# 1. GPU 옵션
# use gpu 레이블
lbl_gpu = Label(frame_option, text="Use GPU", width=8)
lbl_gpu.pack(side="left")

# use gpu 콤보
opt_gpu = ["False", "True"]
cmb_gpu = ttk.Combobox(frame_option, state="readonly", values=opt_gpu, width=10)
cmb_gpu.current(0)
cmb_gpu.pack(side="left", padx=5, pady=5)

# 2. 저장 옵션
# save 옵션 레이블
lbl_save = Label(frame_option, text="Save log", width=8)
lbl_save.pack(side="left", padx=5, pady=5)
# 간격 옵션 콤보
opt_save = ["False", "True"]
cmb_save = ttk.Combobox(frame_option, state="readonly", values=opt_save, width=10)
cmb_save.current(0)
cmb_save.pack(side="left", padx=5, pady=5)

# 3. GradCAM 옵션
lbl_CAM = Label(frame_option, text="Visualize", width=8)
lbl_CAM.pack(side="left")
# 간격 옵션 콤보
opt_CAM = ["False", "True"]
cmb_CAM = ttk.Combobox(frame_option, state="readonly", values=opt_CAM, width=10)
cmb_CAM.current(0)
cmb_CAM.pack(side="left", padx=5, pady=5)


# 진행 상황 Progress bar
frame_progress = LabelFrame(root, text="progress")
frame_progress.pack(fill="x", padx=5, pady=5, ipady=5)

p_var = DoubleVar()
progress_bar = ttk.Progressbar(frame_progress, maximum=100, variable=p_var)
progress_bar.pack(fill="x", padx=5, pady=5)

# 실행 프레임
frame_run = Frame(root)
frame_run.pack(fill="x", padx=5, pady=5)

btn_close = Button(frame_run, padx=5, pady=5, text="Close", width=12, command=root.quit)
btn_close.pack(side='right', padx=5, pady=5)

btn_start = Button(frame_run, padx=5, pady=5, text="Start", width=12, command=start)
btn_start.pack(side='right', padx=5, pady=5)

root.resizable(False, False)
root.config(menu=menu)

root.mainloop()
