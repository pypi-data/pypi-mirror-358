import subprocess
import os
import shlex

def trim_video(video_path, duration):
    """
    Trims the video to the last 3.5 hours if longer than 3.5 hours.
    """
    output_path = os.path.splitext(video_path)[0] + "_trimmed.mp4"
    start_time = max(0, duration - (3.5 * 3600))  # Calculate start time for the last 3.5 hours
    command = f"ffmpeg -y -i {shlex.quote(video_path)} -ss {start_time} -t {3.5 * 3600} -c copy {shlex.quote(output_path)}"
    subprocess.run(command, shell=True)
    os.replace(output_path, video_path)  # Replace original file with trimmed version