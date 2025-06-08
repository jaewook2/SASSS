import subprocess
from pathlib import Path
import shutil
import os


class SemantEncoder ():
    def __init__ (self, input_dir, output_dir_temp, output_dir, fps):
        self.input_dir = input_dir
        self.output_dir_temp = output_dir_temp
        self.output_dir = output_dir
        self.framerate = fps
        
    def folder_init (self, path):
        # Initilize the output folder 
        if os.path.exists(path):
            print ("Remove folders in output folder at ", path)
            shutil.rmtree(path)
        Path(path).mkdir(parents=True, exist_ok=True)

    def add_semantic_tag_to_m3u8(self, m3u8_path, risk_type, risk_leve,bool_privacy = 0):
        # add semantic tag and level tags that are newly defined to m3u8 files
        with open(m3u8_path, "r") as f:
            lines = f.readlines()

        output_lines = []
        inserted = False
        risk_tag = int(risk_leve)

        for line in lines:
            output_lines.append(line)
            # inserts the semantic_type and level tags for the first line.
            if not inserted and line.startswith("#EXTINF:"):
                output_lines.insert(-1, f"#EXT-X-SEMANTICTYPE:{int(risk_type)}\n")
                output_lines.insert(-1, f"#EXT-X-SEMANTICLEVEL:{risk_tag}\n")
                output_lines.insert(-1, f"#EXT-X-PRIVACY:{int(bool_privacy)}\n")

                inserted = True

        # update the m3u8 file with the modified contents 
        with open(m3u8_path, "w") as f:
            f.writelines(output_lines)
        print(f"[✔] Inserted semantic tag: #EXT-X-SEMANTICTYPE:{risk_type} → {m3u8_path}")
        print(f"[✔] Inserted semantic tag: #EXT-X-SEMANTICLEVEL:{risk_tag} → {m3u8_path}")
        print(f"[✔] Inserted semantic tag: #EXT-X-PRIVACY:{bool_privacy} → {m3u8_path}")

        
    def encode_per_folder(self, input_foler_path,risk_type, risk_level,privacy, index, segment_prefix = "720p", scale = "scale=1280:720", start_number=0):
        # encoding the jps images in the input_foler_path to the ts files (with scale)
        # Only one TS file and one M3U8 file are generated in output_temp_path 
        #   (temporary files will be modified and moved later)
        input_pattern = input_foler_path+"/frame%04d.jpg"
                    

        output_temp_path = self.output_dir_temp+'/temp_'+segment_prefix+'_'+privacy +'_'+str(index) 
        self.folder_init(output_temp_path)
        Path(output_temp_path).mkdir(parents=True, exist_ok=True)

        m3u8_path = output_temp_path+ "/"+ f"{segment_prefix}.m3u8"
        segment_pattern = output_temp_path + "/"+ f"{segment_prefix}_%04d.ts"

        # FFmpeg Commend
        cmd = [
            "ffmpeg",
            "-framerate", str(self.framerate),
            "-start_number", str(start_number),
            "-i", input_pattern,
            "-vf", scale,
            "-c:v", "libx264",
            "-b:v", "5000k",
            "-preset", "fast",
            "-pix_fmt", "yuv420p",
            "-hls_time", "10",
            "-hls_segment_filename", segment_pattern,
            "-f", "hls",
            m3u8_path
        ]
        print(f"[▶] Running FFmpeg : {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        print(f"[✔] HLS encoded: {m3u8_path}")
        # update semantic type and level tags to m3u8 file
        if privacy == 'blur': 
            bool_privacy = 1
        else:
            bool_privacy = 0
        
        self.add_semantic_tag_to_m3u8(m3u8_path, risk_type, risk_level, bool_privacy=bool_privacy )    
        
        return output_temp_path
        
    def create_init_m3u8(self, 
                         #playlist_info = [("1080p", "1920x1080", 5000000, False),("720p",  "1280x720",  2800000,False),("480p",  "854x480",   1400000,False)]):
                         playlist_info = [("1080p", "1920x1080", 5000000, False),("720p",  "1280x720",  2800000,False),("480p",  "854x480",   1400000,False), 
                                          ("1080p", "1920x1080", 5000000, True),("720p",  "1280x720",  2800000,True),("480p",  "854x480",   1400000,True)]):

        """
        crate inital m3u8 files in output_dir according to 
        the playlist_info: list of tuples - [(m3u8_filename, resolution_str, bandwidth, privacy_boolean)]
        e.g. [("1080p", "1920x1080", 5000000, False), ("720p", "1280x720", 2800000, False), ...]
        """
        output_dir = Path(self.output_dir)
        master_path = output_dir / "master.m3u8"

        lines = ["#EXTM3U", "#EXT-X-VERSION:3\n"]

        for filename, resolution, bandwidth, privacy in playlist_info:
            if privacy == True:
                lines.append(f"#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},RESOLUTION={resolution},NAME={filename}_privacy")
                filename = filename+"_privacy.m3u8"
            else:     
                lines.append(f"#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},RESOLUTION={resolution},NAME={filename}")
                filename = filename+".m3u8"
            lines.append(filename)
            
            # create initial m3u8 for each resolution
            output_m3u8_path = self.output_dir+"/"+ filename
            with open(output_m3u8_path, "w") as f:
                pass 

        with open(master_path, "w") as f:
            f.write("\n".join(lines) + "\n")

        print(f"[✔] Created master.m3u8 and resoultion.m3u8 files at {master_path}")
        
        
    def update_ts_m3u8(self, temp_folder_path,  file_index, segment_prefix="1080p", privacy = False):
        # move and update ts and m3u8 files 
        # just one ts and m3u8 files exist in temp_folder_path
        src =temp_folder_path + "/"+f"{segment_prefix}_0000.ts"
        ts_index = temp_folder_path.split("_")[-1]

        if privacy == True:
            dst = self.output_dir + "/" + f"{segment_prefix}_{int(ts_index):04d}_privacy.ts"
        else:
            dst = self.output_dir + "/" + f"{segment_prefix}_{int(ts_index):04d}.ts"
        shutil.copyfile(src, dst)

        m3u8_path = temp_folder_path+"/"+ f"{segment_prefix}.m3u8"

        if privacy == True:
            output_m3u8_path = self.output_dir+"/"+ f"{segment_prefix}_privacy.m3u8"
        else:
            output_m3u8_path = self.output_dir+"/"+ f"{segment_prefix}.m3u8"
        
        # update the main m3u8 files        
        if int(ts_index) == 1:
            shutil.copyfile(m3u8_path, output_m3u8_path)
            with open(output_m3u8_path, "r") as f:
                lines = f.readlines()
            original_name = f"{segment_prefix}_{int(0):04d}.ts"
            if privacy:
                privacy_name = f"{segment_prefix}_{int(ts_index):04d}_privacy.ts"
            else:
                privacy_name = f"{segment_prefix}_{int(ts_index):04d}.ts"

            updated_lines = [
                line.replace(original_name, privacy_name)
                for line in lines
            ]
            with open(output_m3u8_path, "w") as f:
                f.writelines(updated_lines)

        else:
            self.append_m3u8_file(m3u8_path, output_m3u8_path,segment_prefix, ts_index, privacy = privacy)
        
    # m3u8 파일 업데이트
    def append_m3u8_file(self, m3u8_path, output_m3u8_path, segment_prefix, ts_index, privacy = False):
        with open(m3u8_path, "r") as f:
            lines = f.readlines()

        for i in range(len(lines)):
            if lines[i].startswith("#EXT-X-SEMANTICTYPE"):
                if i + 4 <= len(lines):
                    risk_type_line ='\n'+lines[i].strip()+'\n'
                    risk_level_line =lines[i+1].strip()+'\n'
                    privacy_line = lines[i+2].strip()+'\n'
                    extinf_line = lines[i+3].strip()+'\n'
                    if privacy:
                        ts_line = f"{segment_prefix}_{int(ts_index):04d}_privacy.ts\n"
                    else:
                        ts_line = f"{segment_prefix}_{int(ts_index):04d}.ts\n"
                    output_lines=[risk_type_line, risk_level_line, privacy_line, extinf_line, ts_line]
        

        # 기존 출력 파일에서 #EXT-X-ENDLIST 제거
        with open(output_m3u8_path, "r") as f:
            existing = f.readlines()
        if existing and existing[-1].strip() == "#EXT-X-ENDLIST":
            existing = existing[:-1]
        # 다시 저장: 기존 내용 + 새로 추가 + ENDLIST
        with open(output_m3u8_path, "w") as f:
            f.writelines(existing + output_lines)
            f.write("#EXT-X-ENDLIST\n")

        print(f"[✔] Appended {m3u8_path} → {output_m3u8_path}")


            
    def encoding (self, folder_names, encoding_list = [("1080p","scale=1920:1080" ),("720p","scale=1280:720" ),("480p","scale=854:480" )]):
        start_number = 0
        
        self.folder_init(self.output_dir_temp)
        self.folder_init(self.output_dir)
        # create master m3u8
        self.create_init_m3u8()

        for folder_name in folder_names:
            risk_level = folder_name.split("_")[-1]
            risk_type = folder_name.split("_")[-2]
            privacy = folder_name.split("_")[-3]
            file_index =  folder_name.split("_")[-4]
            bool_privacy = False
            if privacy == "blur":
                bool_privacy = True

            input_foler_path = self.input_dir + "/" + folder_name
            
            for segment_prefix, scale in encoding_list:
              # 확질 별로 디코딩 : temp folder에 생성
                temp_folder_path = self.encode_per_folder(input_foler_path, risk_type, risk_level,privacy, file_index, segment_prefix=segment_prefix, scale=scale, start_number=0)
                self.update_ts_m3u8(temp_folder_path, file_index,  segment_prefix=segment_prefix, privacy = bool_privacy)
        return file_index 

