
# pip install pandas openpyxl
import pandas as pd
import os
import shutil
from pathlib import Path

def preProcessing (input_dir, output_dir, fps, max_chunk_duration):
    # 1. xlsx 파일을 통해 [(frame, risk)] 정보를 리스트 형태로 파싱
    #  - 리스크 정보와 jpg 파일을 input_dir에 있다고 가정
    semantic_df = pd.read_excel("input_dir/semantic_info.xlsx")
    frame_risk_list = list(zip(semantic_df["filename"], semantic_df["risk_level"]))
    max_chunks = fps*max_chunk_duration

    pass

def splitSegements(frame_risk_list, max_chunks,output_dir,input_dir):
   dir_iter = 0
   file_index = 0
   dir_boolen = False
   dir_name = None
   current_segments = []
   lask_rist  = -1
# 수정 할 것 0602
   for filename, risk in frame_risk_list:
       file_index = file_index+1

       if risk != last_risk or len(current_segments) >= max_chunks:
           dir_iter = dir_iter+1
           frames_name = f"segment_{dir_iter:04d}_{risk}"
           # 폴더 만들기
           frames_path = output_dir+"/"+frames_name
           frames_path.mkdir(parents=True, exist_ok=True)
           current_segments=[]

       current_segments.append(filename)
       src = Path(input_dir) / fname
       dst = frames_path / f"frame{file_index:04d}.jpg"
       shutil.copyfile(src, dst)
       last_risk = risk


