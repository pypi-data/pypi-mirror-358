from PIL import Image
import shutil
import os

class Scene:
    def __init__(self, duration=5, bg_color="#ffffff", size=(1920, 1080), fps=30):
        self.duration = duration
        self.bg_color = bg_color
        self.size = size
        self.fps = fps
        self.frames = []
    def render(self, output="output.mp4"):
        os.makedirs("_frames", exist_ok=True)
        total = int(self.duration * self.fps)
        for i in range(total):
            frame = Image.new("RGB", self.size, self.bg_color)
            self.frames.append(frame)
            frame.save(os.path.join("_frames", f"frame_{i:04d}.png"))
        print(f"Rendering {total} frames...")
        os.system(
            f"ffmpeg -framerate {self.fps} -i _frames/frame_%04d.png -c:v libx264 -pix_fmt yuv420p {output}"
        )
        shutil.rmtree("_frames")