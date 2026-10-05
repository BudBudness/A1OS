from pathlib import Path
import subprocess

def render_color_clip(output: str, seconds: int = 1, width: int = 1280, height: int = 720) -> str:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg","-y","-f","lavfi","-i",f"color=c=black:s={width}x{height}:r=30:d={seconds}","-pix_fmt","yuv420p",str(path)],check=True)
    return str(path)
