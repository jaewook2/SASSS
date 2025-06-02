import subprocess
from pathlib import Path
def encode_per_folder(input_dir, output_dir, segment_prefix = "720p", scale = "scale=1280:720", start_number=0, framerate=25):
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

def encoding (input_dir, folder_names, output_dir, fps)
    start_number = 0
    for folder_name in folder_names:
        input_path = input_dir + "/" + folder_name
        output_path =  output_dir

        encode_per_folder(input_path, output_path, segment_prefix="1080p", scale="scale=1920:1080", start_number=0, framerate=fps):
        encode_per_folder(input_path, output_path, segment_prefix="720p", scale="scale=1280:720", start_number=0, framerate=fps):
        encode_per_folder(input_path, output_path, segment_prefix="480p", scale="scale=854:480", start_number=0,  framerate=fps):

        # m3u8 update
