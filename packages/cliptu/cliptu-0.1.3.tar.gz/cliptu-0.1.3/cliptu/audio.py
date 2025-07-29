import os
from utils.utils import *
import shlex
import subprocess

def convert_opus_to_aac(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".mp4"):
            input_path = os.path.join(directory, filename)
            output_path = os.path.join(directory, f"converted_{filename}")
            
            # Construct the ffmpeg command with additional options for analysis
            command = (
                f"ffmpeg -y -analyzeduration 100M -probesize 50M -i {shlex.quote(input_path)} "
                f"-c:v copy -c:a aac -b:a 128k -async 1 -fps_mode vfr {shlex.quote(output_path)}"
            )
            
            # Execute the command
            subprocess.run(command, shell=True, check=True)
            print(f"Converted {filename} to {output_path}")

def mp4_to_aac(video_path):
    """
    Converts a video file to an AAC audio file using ffmpeg.

    Parameters:
    video_path (str): The file path of the input video.

    Returns:
    str: The file path for the output AAC audio.
    """

    # Assuming you want to keep the original file name but change the extension to .aac
    audio_path = f"{os.path.splitext(video_path)[0]}.aac"
    escaped_video_path = shlex.quote(video_path)
    escaped_audio_path = shlex.quote(audio_path)

    # Command updated to use AAC codec. The '-acodec aac' specifies the audio codec.
    # Removed '-ar 44100 -ac 2' assuming default AAC settings, but you can include these for specific sampling rate and channel count
    command = f"ffmpeg -y -loglevel error -hwaccel cuda -hwaccel_output_format cuda -i {escaped_video_path} -vn -acodec aac {escaped_audio_path}"

    os.system(command)
    return audio_path

def get_audio_codec(video_path):
    """Uses ffprobe to determine the audio codec of the given video file."""
    command = f"ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 {shlex.quote(video_path)}"
    codec = subprocess.run(command, shell=True, text=True, capture_output=True).stdout.strip()
    return codec

def video_to_audio(video_path):
    """
    Converts a video file to an audio file using ffmpeg. The output format is determined by the audio codec of the video file.

    Note: May output opus which breaks pyannotes segmentation model

    Parameters:
    video_path (str): The file path of the input video.

    Returns:
    str: The file path of the output audio file.
    """
    codec = get_audio_codec(video_path)
    # Define a mapping from common codecs to file extensions
    codec_to_extension = {
        'aac': 'aac',
        'mp3': 'mp3',
        'vorbis': 'ogg',
        'opus': 'opus',
        'pcm_s16le': 'wav'  # assuming WAV for PCM
    }
    audio_extension = codec_to_extension.get(codec, 'wav')  # default to WAV if codec is unknown

    base = os.path.splitext(video_path)[0]
    audio_path = f"{base}.{audio_extension}"
    
    print('Converting video to audio ----------------')
    escaped_video_path = shlex.quote(video_path)
    escaped_audio_path = shlex.quote(audio_path)
    command = f"ffmpeg -y -i {escaped_video_path} -vn -acodec copy {escaped_audio_path}"
    os.system(command)
    
    return audio_path

def mp4_to_wav(video_path):
    """
    Converts a video file to an audio file using ffmpeg.

    Parameters:
    video_path (str): The file path of the input video.
    audio_path (str): The file path for the output audio.
    """

    audio_path = f"{everything_before_extension(video_path)}.wav"
    escaped_video_path = shlex.quote(video_path)
    escaped_audio_path = shlex.quote(audio_path)
    #command = f"ffmpeg -#y -i {escaped_video_path} -vn -acodec pcm_s16le -ar 44100 -ac 2 {escaped_audio_path}"
    print('mp4 to wav ----------------')
    command = f"ffmpeg -y -loglevel error -hwaccel cuda -hwaccel_output_format cuda -i {escaped_video_path} -vn -acodec pcm_s16le -ar 44100 -ac 2 {escaped_audio_path}"

    os.system(command)
    return audio_path

if __name__ == '__main__':
  audio_path = mp4_to_wav('/home/ubuntu/cliptu/backend/test/videos/hikaru_130.mp4')
  print(audio_path)