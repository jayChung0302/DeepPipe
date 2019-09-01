import pandas as pd
import numpy as np

def main():
    pass

if __name__ == '__main__':
    print("activate right")
    excel_name = 'C:/Users/lenovo/Dropbox/PROJECT/Sewer Pipe/location_information/관로 이상항목별 동영상 재생위치 - 김포.xlsx'
    df = pd.read_excel(excel_name, sheet_name=0)
    cctv_name = list(df['Unnamed: 1'])
    defect_name = list(df['Unnamed: 2'])
    defect_time = list(df['Unnamed: 3'])
    defect_dic = {}
    for i, k in enumerate(zip(cctv_name, defect_name, defect_time)):
        a, b, c = k
        if i == 0:
            continue
        if b not in defect_dic:
            print(b, i)
            defect_dic[b] = 1
        defect_dic[b] = defect_dic[b] + 1