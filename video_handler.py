import subprocess
import json
import os

class VideoHandler:
    def __init__(self, file_path):
        self.file_path = file_path

    def get_metadata(self):
        """Returns metadata of the video file using ffprobe."""
        try:
            cmd = [
                'ffprobe', 
                '-v', 'quiet', 
                '-print_format', 'json', 
                '-show_format', 
                self.file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return {}
            
            data = json.loads(result.stdout)
            return data.get('format', {}).get('tags', {})
        except Exception:
            return {}

    def update_metadata(self, key, value, output_path=None):
        """Updates or adds a metadata tag using ffmpeg."""
        if output_path is None:
            output_path = f"mod_{os.path.basename(self.file_path)}"
        
        try:
            # ffmpeg -i input -metadata key=value -codec copy output
            cmd = [
                'ffmpeg',
                '-y', # Overwrite output
                '-i', self.file_path,
                '-metadata', f"{key}={value}",
                '-codec', 'copy',
                output_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return output_path
            else:
                raise Exception(f"FFmpeg error: {result.stderr}")
        except Exception as e:
            raise e

    @staticmethod
    def is_video(file_path):
        ext = os.path.splitext(file_path)[1].lower()
        return ext in ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm']
