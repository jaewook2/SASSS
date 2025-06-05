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
        if os.path.exists(path):
            print ("Remove folders in output_dir of preprocessing", path)
            shutil.rmtree(path)
        Path(path).mkdir(parents=True, exist_ok=True)

    def add_semantic_tag_to_m3u8(self, m3u8_path, risk_tag):
        with open(m3u8_path, "r") as f:
            lines = f.readlines()

        output_lines = []
        inserted = False

        for line in lines:
            output_lines.append(line)
            # 첫 번째 세그먼트 앞에 삽입
            if not inserted and line.startswith("#EXTINF:"):
                output_lines.insert(-1, f"#SEMANTIC-RISK-LEVEL:{risk_tag}\n")
                inserted = True

        # 다시 저장
        with open(m3u8_path, "w") as f:
            f.writelines(output_lines)

        print(f"[✔] Inserted semantic tag: #SEMANTIC-RISK:{risk_tag} → {m3u8_path}")
        
    def encode_per_folder(self, input_foler_path, risk_level, index, segment_prefix = "720p", scale = "scale=1280:720", start_number=0):
        # 프레임 입력 경로
        input_pattern = input_foler_path+"/frame%04d.jpg"

        # 출력 경로 설정
        output_temp_path = self.output_dir_temp+'/temp_'+segment_prefix+'_'+str(index) 
        self.folder_init(output_temp_path)
        Path(output_temp_path).mkdir(parents=True, exist_ok=True)

        # 출력 파일명 구성
        m3u8_path = output_temp_path+ "/"+ f"{segment_prefix}.m3u8"
        segment_pattern = output_temp_path + "/"+ f"{segment_prefix}_%04d.ts"

        # FFmpeg 명령어 구성
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
        # update semantic info
        self.add_semantic_tag_to_m3u8(m3u8_path, risk_level)    
        
        return output_temp_path
        
    def create_init_m3u8(self, playlist_info = [("1080p.m3u8", "1920x1080", 5000000),("720p.m3u8",  "1280x720",  2800000),("480p.m3u8",  "854x480",   1400000)]):
        """
        output_dir: str or Path - master.m3u8을 생성할 폴더
        playlist_info: list of tuples - [(m3u8_filename, resolution_str, bandwidth)]
        e.g. [("1080p.m3u8", "1920x1080", 5000000), ("720p.m3u8", "1280x720", 2800000), ...]
        """
        output_dir = Path(self.output_dir)
        master_path = output_dir / "master.m3u8"

        lines = ["#EXTM3U", "#EXT-X-VERSION:3\n"]

        for filename, resolution, bandwidth in playlist_info:
            lines.append(f"#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},RESOLUTION={resolution}")
            lines.append(filename)
            
            # create initial m3u8 for each resolution
            output_m3u8_path = self.output_dir+"/"+ filename
            with open(output_m3u8_path, "w") as f:
                pass 

        with open(master_path, "w") as f:
            f.write("\n".join(lines) + "\n")

        print(f"[✔] Created master.m3u8 at {master_path}")
        
        
    def update_ts_m3u8(self, temp_folder_path,  file_index, segment_prefix="1080p"):
        # ts 파일 이동 // 파일 명 순차적으로 변경
        src =temp_folder_path + "/"+f"{segment_prefix}_0000.ts"
        ts_index = temp_folder_path.split("_")[-1]
        dst = self.output_dir + "/" + f"chunk_{segment_prefix}_{int(ts_index):04d}.ts"
        shutil.copyfile(src, dst)

        # m3u8 파일 업데이트 + risk 정보 업데이트
        m3u8_path = temp_folder_path+"/"+ f"{segment_prefix}.m3u8"
        output_m3u8_path = self.output_dir+"/"+ f"{segment_prefix}.m3u8"
        
        if int(ts_index) == 0:
            shutil.copyfile(m3u8_path, output_m3u8_path)
        else:
            self.append_m3u8_file(m3u8_path, output_m3u8_path,segment_prefix, ts_index)
        
    # m3u8 파일 업데이트
    def append_m3u8_file(self, m3u8_path, output_m3u8_path, segment_prefix, ts_index):
        with open(m3u8_path, "r") as f:
            lines = f.readlines()

        for i in range(len(lines)):
            if lines[i].startswith("#SEMANTIC-RISK-LEVEL"):
                if i + 2 <= len(lines):
                    risk_line ='\n'+lines[i].strip()+'\n'
                    extinf_line = lines[i+1].strip()+'\n'
                    ts_line = f"chunk_{segment_prefix}_{int(ts_index):04d}.ts\n"
                    output_lines=[risk_line, extinf_line, ts_line]
                    print(output_lines)
        

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


            
    def encoding (self, folder_names, encoding_list = [("1080p","scale=1920:1080" ),("720p","scale=1280:720" ),("480p","scale=854:480" ) ]):
        start_number = 0
        file_index = 0
        self.folder_init(self.output_dir_temp)
        self.folder_init(self.output_dir)
        # create master m3u8
        self.create_init_m3u8()

        for folder_name in folder_names:
            risk_level = folder_name.split("_")[-1]
            print (folder_name)
            print (risk_level)

            input_foler_path = self.input_dir + "/" + folder_name
            
            for segment_prefix, scale in encoding_list:
              # 확질 별로 디코딩 : temp folder에 생성
                temp_folder_path = self.encode_per_folder(input_foler_path, risk_level, file_index, segment_prefix=segment_prefix, scale=scale, start_number=0)
                print (temp_folder_path)
                self.update_ts_m3u8(temp_folder_path, file_index,  segment_prefix=segment_prefix)
            file_index = file_index+1
            '''
            self.encode_per_folder(input_foler_path, risk_level, file_index,segment_prefix="720p", scale="scale=1280:720", start_number=0)
            #update_ts_m3u8(file_index,  segment_prefix="720p")
            self.encode_per_folder(input_foler_path,risk_level,file_index,  segment_prefix="480p", scale="scale=854:480", start_number=0)
            #update_ts_m3u8(file_index,  segment_prefix="480p")
            '''

'''







'''



            # output folder로 이동 및 index 변경

            # m3u8 update
        

