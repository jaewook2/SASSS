
# pip install pandas openpyxl
import pandas as pd
import os
import shutil
from pathlib import Path
import subprocess

class SemantPreprocessor ():
    def __init__ (self, input_dir_pre, output_dir_pre, fps, max_chunk_duration, semantic_fname):
        self.input_dir = input_dir_pre
        self.output_dir = output_dir_pre
        
        self.fps = fps
        self.max_duration = max_chunk_duration  
        self.max_images = fps*max_chunk_duration
        self.semantic_fname = semantic_fname
        
    def folder_init (self):
        if os.path.exists(self.output_dir):
            print ("Remove folders in output_dir of preprocessing", self.output_dir)
            shutil.rmtree(self.output_dir)
        
    def load_semantic_info (self, semantic_fname = None):
        # According to the data format of semantic_info, this f should be updated
        # semantic_df = pd.read_excel(self.input_dir+semantic_fname)
        if semantic_fname == None:
            semantic_fname = self.semantic_fname
        semantic_df = pd.read_csv(self.input_dir+"/"+semantic_fname)

        frame_risk_list = list(zip(semantic_df["frame"], semantic_df["risk"], semantic_df["level"]))
        return frame_risk_list
    
    def splitSegemnt(self, filename, risk, level, folder_index, file_index, new_folder = False, privacy = False):
        # Create New folder for aggreating the jpg files based on risk or max_images
        if privacy == False:
            folder_name = f"segment_{folder_index:04d}_clear_{risk}_{level}"
        else:
            folder_name = f"segment_{folder_index:04d}_blur_{risk}_{level}"

        folder_path = self.output_dir+"/"+folder_name

        if new_folder:
            Path(folder_path).mkdir(parents=True, exist_ok=True)
        
        if privacy:
           # src = self.input_dir + "/frame_blur/" + filename 
            src = self.input_dir + "/frame/" + filename # to be changed with above line when blur images are used
        else:
            src = self.input_dir + "/frame/" + filename
        
        dst = folder_path + "/" + f"frame{file_index:04d}.jpg"
        shutil.copyfile(src, dst)
        
        return folder_name


    def splitSegements_all(self, frame_risk_list, privacy=False):
        folder_index = 0
        file_index = 0
        last_level  = -1
        folder_names =[]
        imageList_in_folder = []
        images_folder_list = []

        for filename, risk, level in frame_risk_list:
            if level != last_level or len(imageList_in_folder) >= self.max_images:
                if len(imageList_in_folder) != 0:
                    images_folder_list.append(imageList_in_folder)
                file_index = 0
                folder_index = folder_index+1
                folder_name = self.splitSegemnt(filename, risk,level, folder_index, file_index, new_folder = True, privacy=privacy)
                folder_names.append(folder_name)
                imageList_in_folder = [filename]
            else :
                file_index = file_index+1
                _ = self.splitSegemnt(filename, risk, level, folder_index, file_index, new_folder = False, privacy=privacy)
                imageList_in_folder.append(filename)
            
            last_level = level
        np.save(self.output_dir +'/foldername.npy', np.array (folder_names))

        return folder_names, images_folder_list


    def preProcessing_all (self, semantic_fname = None, privacy=False):
        if  semantic_fname == None:
            semantic_fname = self.semantic_fname
        semantic_df = self.load_semantic_info(semantic_fname)
        frame_risk_list = list(zip(semantic_df["frame"], semantic_df["risk"], semantic_df["level"]))

        folder_names, images_folder_list = self.splitSegements_all(frame_risk_list,privacy=privacy)
        return folder_names, images_folder_list







# input drectory name : input_dir
# folder names list : fname_list
