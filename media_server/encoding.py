import subprocess
from pathlib import Path
import shutil

def add_semantic_tag_to_m3u8(m3u8_path, risk_tag):
    with open(m3u8_path, "r") as f:
        lines = f.readlines()

    output_lines = []
    inserted = False

    for line in lines:
        output_lines.append(line)
        # 첫 번째 세그먼트 앞에 삽입
        if not inserted and line.startswith("#EXTINF:"):
            output_lines.insert(-1, f"#SEMANTIC-RISK:{risk_tag}\n")
            inserted = True

    # 다시 저장
    with open(m3u8_path, "w") as f:
        f.writelines(output_lines)

    print(f"[✔] Inserted semantic tag: #SEMANTIC-RISK:{risk_tag} → {m3u8_path}")

def encode_per_folder(input_dir, output_dir, risk_level, segment_prefix = "720p", scale = "scale=1280:720", start_number=0, framerate=25):
    # 프레임 입력 경로
    input_pattern = str(Path(input_dir) / "frame%04d.jpg")

    # 출력 경로 설정
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 출력 파일명 구성
    m3u8_path = output_path / f"{segment_prefix}.m3u8"
    segment_pattern = output_path / f"{segment_prefix}_%04d.ts"

    # FFmpeg 명령어 구성
    cmd = [
        "ffmpeg",
        "-framerate", str(framerate),
        "-start_number", str(start_number),
        "-i", input_pattern,
        "-vf", scale,
        "-c:v", "libx264",
        "-b:v", "5000k",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-hls_time", "10",
        "-hls_segment_filename", str(segment_pattern),
        "-f", "hls",
        str(m3u8_path)
    ]
    print(f"[▶] Running FFmpeg : {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"[✔] HLS encoded: {m3u8_path}")
    # update semantic info
    add_semantic_tag_to_m3u8(m3u8_path, risk_level)


def append_m3u8_file(m3u8_path, output_m3u8_path):
    # 원본 파일에서 내용 읽기
    with open(m3u8_path, "r") as f:
        lines_to_append = f.readlines()

    # #EXT-X-ENDLIST 제거
    if lines_to_append and lines_to_append[-1].strip() == "#EXT-X-ENDLIST":
        lines_to_append = lines_to_append[:-1]

    # 출력 파일이 없으면 헤더 포함 전체 생성
    if not Path(output_m3u8_path).exists():
        with open(output_m3u8_path, "w") as f:
            f.writelines(lines_to_append)
            f.write("#EXT-X-ENDLIST\n")
    else:
        # 기존 출력 파일에서 #EXT-X-ENDLIST 제거
        with open(output_m3u8_path, "r") as f:
            existing = f.readlines()
        if existing and existing[-1].strip() == "#EXT-X-ENDLIST":
            existing = existing[:-1]
        # 다시 저장: 기존 내용 + 새로 추가 + ENDLIST
        with open(output_m3u8_path, "w") as f:
            f.writelines(existing + lines_to_append)
            f.write("#EXT-X-ENDLIST\n")

    print(f"[✔] Appended {m3u8_path} → {output_m3u8_path}")



def update_ts_m3u8(output_temp, output_path,  file_index, segment_prefix="1080p"):
    # ts 파일 이동 // 파일 명 순차적으로 변경
    src = output_temp / f"{segment_prefix}_%04d.ts"
    # dst = folder_path + "/" + f"frame{file_index:04d}_{risk}.jpg"
    dst = output_path + "/" + f"frame_{segment_prefix}_{file_index:04d}.ts"
    shutil.copyfile(src, dst)

    # m3u8 파일 업데이트 + risk 정보 업데이트
    m3u8_path = output_temp+"/"+ f"{segment_prefix}.m3u8"
    output_m3u8_path = output_path+" /"+ f"{segment_prefix}.m3u8"
    append_m3u8_file(m3u8_path, output_m3u8_path)


def encoding (input_dir, folder_names, output_dir, fps):
    start_number = 0
    file_index = 0
    for folder_name in folder_names:
        risk_level = folder_name.split("_")[-1]

        input_path = input_dir + "/" + folder_name
        output_temp =  "temp_folder"

        # 확질 별로 디코딩 : temp folder에 생성
        encode_per_folder(input_path, output_temp, risk_level,  segment_prefix="1080p", scale="scale=1920:1080", start_number=0, framerate=fps)
        update_ts_m3u8(output_temp, output_dir, file_index,  segment_prefix="1080p")
        encode_per_folder(input_path, output_temp, risk_level, segment_prefix="720p", scale="scale=1280:720", start_number=0, framerate=fps)
        update_ts_m3u8(output_temp, output_dir, file_index,  segment_prefix="720p")
        encode_per_folder(input_path, output_temp,risk_level,  segment_prefix="480p", scale="scale=854:480", start_number=0,  framerate=fps)
        update_ts_m3u8(output_temp, output_dir, file_index,  segment_prefix="480p")

        file_index = file_index+1

        # output folder로 이동 및 index 변경

        # m3u8 update
        

