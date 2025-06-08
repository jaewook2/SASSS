
# pip install pandas openpyxl
from raPreprocessor import *
from raEncoder import *
from semanticEncoder import *
import numpy as np


preprocTest = True
encoderTest = True
s_encoderTest = False
## Preprocess Testing
if preprocTest == True:
    input_dir_pre = "../../input"
    output_dir_pre = "./output/frames"
    fps = 30 # 정확히 확인 필요
    max_chunk_duration = 5 
    semantic_fname =  "output.csv"
    franmaes_dir = './output/frames/foldername.npy'

    prepro = SemantPreprocessor(input_dir_pre, output_dir_pre, fps, max_chunk_duration, semantic_fname)
    prepro.folder_init()
    # testing semantic info
    frame_risk_list = prepro.load_semantic_info()
    
    privacy = True
    folder_index = 0
    file_index = 0
    last_level  = -1
    imageList_in_folder = []
    images_folder_list = []
    folder_names =[]
    for filename, risk, level in frame_risk_list:
        if level != last_level or len(imageList_in_folder) >= prepro.max_images:
            if len(imageList_in_folder) != 0:
                images_folder_list.append(imageList_in_folder) 
                # Here encoding gogo
            file_index = 0
            folder_index = folder_index+1
            folder_name = prepro.splitSegemnt(filename, risk,level, folder_index, file_index, new_folder = True,privacy = False)
            folder_names.append(folder_name)
            imageList_in_folder = [filename]
        else :
            file_index = file_index+1
            _ = prepro.splitSegemnt(filename, risk, level, folder_index, file_index, new_folder = False, privacy =False)
            imageList_in_folder.append(filename)
            
        last_level = level
        
    if privacy == True:
        folder_index = 0
        file_index = 0
        last_level  = -1
        imageList_in_folder = []
        images_folder_list_pri = []
        folder_names_pri =[]
        for filename, risk, level in frame_risk_list:
            if level != last_level or len(imageList_in_folder) >= prepro.max_images:
                if len(imageList_in_folder) != 0:
                    images_folder_list.append(imageList_in_folder) 
                    # Here encoding gogo
                file_index = 0
                folder_index = folder_index+1
                folder_name = prepro.splitSegemnt(filename, risk,level, folder_index, file_index, new_folder = True,privacy = privacy)
                folder_names_pri.append(folder_name)
                imageList_in_folder = [filename]
            else :
                file_index = file_index+1
                _ = prepro.splitSegemnt(filename, risk, level, folder_index, file_index, new_folder = False, privacy = privacy)
                imageList_in_folder.append(filename)
                
            last_level = level
        folder_names_clear = folder_names
        folder_names = []
        for index in range(len(folder_names_clear)):
            folder_names.append(folder_names_clear[index])
            folder_names.append(folder_names_pri[index])

        folder_names = folder_names+folder_names_pri
    np.save(franmaes_dir, np.array (folder_names))

    #print (folder_names)
    #print (images_folder_list)
if encoderTest == True:
    input_dir = "./output/frames"
    output_dir_temp = "./output/temp"
    #output_dir_main = "/usr/local/nginx/html/stream/hls"
    output_dir_main = "./output/main"
    franmaes_dir = './output/frames/foldername.npy'
    fps = 30 # 정확히 확인 필요

    encoder = SemantEncoder(input_dir, output_dir_temp, output_dir_main, fps)
    folder_names = np.load(franmaes_dir)
    print (folder_names)
    encoder.encoding(folder_names)

if s_encoderTest == True:
    pass
    '''
    input_dir_pre = "../../input"
    output_dir_pre = "./output/frames"
    fps = 30 # 정확히 확인 필요
    max_chunk_duration = 5 
    semantic_fname =  "output.csv"
    
    input_dir_encode = "./output/frames"
    output_dir_encode_temp = "./output/temp"
    output_dir_encode_main = "/usr/local/nginx/html/stream/hls"

    s_semanticEncoder= semanticEncoder(input_dir_pre, output_dir_pre, fps, max_chunk_duration, semantic_fname, input_dir_encode, output_dir_encode_temp, output_dir_encode_main)
    s_semanticEncoder.encoding_all()
    '''
    
    
    