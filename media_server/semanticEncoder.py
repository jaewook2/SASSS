from raPreprocessor import *
from raEncoder import *
import numpy as np

class semanticEncoder ():
    def __init__ (self, input_dir_pre, output_dir_pre, fps, max_chunk_duration, semantic_fname, input_dir_encode, output_dir_encode_temp, output_dir_encode_main):
        self.prepro = SemantPreprocessor(input_dir_pre, output_dir_pre, fps, max_chunk_duration, semantic_fname)
        self.encoder = SemantEncoder(input_dir_encode, output_dir_encode_temp, output_dir_encode_main, fps)
        self.output_dir_pre = output_dir_pre 
        
    def encoding_all (self, enable_pre = True):
        if enable_pre == True:
            folder_names, images_folder_list = self.prepro.preProcessing_all()
        else:
            folder_names = np.load( self.output_dir_pre+'/foldername.npy')
            self.encoder.encoding(folder_names)
    
    def encoding_realtime(self):
        pass 
        '''
        self.prepro.folder_init()
        # testing semantic info
        frame_risk_list = self.prepro.load_semantic_info()
        file_index = 0
        last_level = -1
        imageList_in_fold=[]
        for filename, risk, level in frame_risk_list:
            if level != last_level or len(imageList_in_folder) >= prepro.max_images:
                if len(imageList_in_folder) != 0:
                    images_folder_list.append(imageList_in_folder) 
                    # Here encoding gogo
                    file_index = self.encoder.encoding([folder_name], file_index = file_index)
                    
                file_index = 0
                folder_index = folder_index+1
                folder_name = prepro.splitSegemnt(filename, risk,level, folder_index, file_index, new_folder = True,privacy = privacy)
                folder_names.append(folder_name)
                imageList_in_folder = [filename]
            else :
                file_index = file_index+1
                _ = prepro.splitSegemnt(filename, risk, level, folder_index, file_index, new_folder = False, privacy = privacy)
                imageList_in_folder.append(filename)
                
            last_level = level
        '''



    