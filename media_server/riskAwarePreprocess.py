
# pip install pandas openpyxl
import pandas as pd
import os
import shutil
from pathlib import Path
import subprocess

def splitSegements(frame_risk_list, max_chunks,output_dir,input_path):
   folder_index = 0
   file_index = 0
   chunks_in_folder = []
   last_risk  = -1
   folder_names =[]
# 수정 할 것 0602
   for filename, risk in frame_risk_list:
       if risk != last_risk or len(chunks_in_folder) >= max_chunks:
           file_index = 0
           folder_index = folder_index+1
           folder_name = f"segment_{folder_index:04d}_{risk}"
           # 폴더 만들기
           folder_path = output_dir+"/"+folder_name
           folder_path.mkdir(parents=True, exist_ok=True)
           chunks_in_folder =[] ## save folder list
           folder_names.append(folder_name)

       file_index = file_index + 1
       chunks_in_folder.append(filename)
       src = input_path + "/" + filename
       #dst = folder_path + "/" + f"frame{file_index:04d}_{risk}.jpg"
       dst = folder_path + "/" + f"frame{file_index:04d}_{risk}.jpg"
       shutil.copyfile(src, dst)
       last_risk = risk


   return folder_names


def preProcessing (input_dir, output_dir, fps, max_chunk_duration):
    # 1. xlsx 파일을 통해 [(frame, risk)] 정보를 리스트 형태로 파싱
    #  - 리스크 정보와 jpg 파일을 input_dir에 있다고 가정
    semantic_df = pd.read_excel("input_dir/semantic_info.xlsx")
    frame_risk_list = list(zip(semantic_df["filename"], semantic_df["risk_level"]))
    max_chunks = fps*max_chunk_duration

    splitSegements(frame_risk_list, max_chunks, output_dir, input_dir)




# input drectory name : input_dir
# folder names list : fname_list
