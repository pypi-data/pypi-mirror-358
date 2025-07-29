import subprocess
import shlex
import os

def video_length_less_than_4_hours(video_path):
    """
    Checks the video length using FFmpeg via os.system and exits the script if it's more than 4 hours.

    Parameters:
    video_path (str): The file path of the video.
    """
    # Creating a command that uses ffprobe (part of FFmpeg) to get the video duration
    # and checks if it's greater than 4 hours (14400 seconds), then exits if true.
    video_path=shlex.quote(video_path)
    #command = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {video_path} | awk '{{if ($1 > 14400) exit 1}}'"
    # Doing 3.5 hours because still crashing with 4
    command = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {video_path} | awk '{{if ($1 > 12600) exit 1}}'"
    
    # Using os.system to execute the command. Note: os.system returns the exit status (0 for success).
    # By design, the command above exits with status 1 if the condition is met (video longer than 4 hours).
    status = os.system(command)
    
    # Checking the status. If the command exited with status 1, it means the video is longer than 4 hours.
    if status:
        print(f"{video_path} is longer than 4 hours. Exiting...")
        # add video to incomplete
        return False
    else:
       return True

def get_video_length(video_path):
    """
    Returns the duration of the video in seconds and prints it in hh:mm:ss format.

    Args:
        video_path (str): Path to the video file.

    Returns:
        float: The duration of the video in seconds.
    """
    try:
        # Construct the ffprobe command
        command = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {shlex.quote(video_path)}"
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        
        # Get duration in seconds
        duration_seconds = float(result.stdout.strip())
        
        # Convert to hh:mm:ss
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = int(duration_seconds % 60)
        duration_hhmmss = f"{hours:02}:{minutes:02}:{seconds:02}"
        
        print(f"Video duration: {duration_seconds:.2f} seconds ({duration_hhmmss})")
        return duration_seconds
    except Exception as e:
        print(f"Error retrieving video length: {e}")
        return 0.0
