from cliptu.ffmpeg import *
import cliptu.ffprobe as ffprobe
import utils.utils as utils
import os

def filter_video(video_path, file_tracking_incomplete):
  if ffprobe.video_length_less_than_4_hours(video_path):
    return True
  else:
    add_to_processed(video_path, file_tracking_incomplete)
    return False

def print_completed(file):
  print(utils.pl(file))

def add_to_processed(name, file_path):
    """
    Check if the completed videos file exists for a channel, and if not, initialize it with an empty set.
    Then, add a video to the set of completed videos and save the updated set.
    """
    
    # Check if the file exists
    if os.path.exists(file_path):
        names = utils.pl(file_path)
    else:
        names = set()  # Initialize with an empty set if file doesn't exist

    # Add the video file name to the set
    names.add(name)

    # Save the updated set back to the file
    utils.pd(names, file_path)

def has_been_processed(name, file_path):
  if os.path.exists(file_path):
    completed = utils.pl(file_path)
  else:
    completed = set()
  return name in completed


################################################################################
# path util functions
################################################################################

def get_transcription_paths(channel):
  """
  Return all transcriptions for a channel (paths)
  Depth is 2, where each speaker in each video gets their own list

  returns:
  [
    [
     channel/<video1>/video_data/transcriptions/speaker1/1.json,
     channel/<video1>/video_data/transcriptions/speaker1/2.json,
     ... 
    ],
    [
     channel/<video1>/video_data/transcriptions/SPEAKER2/1.json,
    ...
    ],
    [
     channel/<video2>/video_data/transcriptions/SPEAKER1/1.json,
     channel/<video2>/video_data/transcriptions/SPEAKER1/2.json,
    ]
  ]
  """
  video_data_paths = get_video_data_paths(channel)
  transcription_paths = []
  for video_data_path in video_data_paths:
    for speaker_path in ls(opj(video_data_path,'transcriptions')):
      transcription_paths.append(ls(speaker_path))
  return transcription_paths
  """
    for all speakers
  parent_folder = f'{video_data_path}transcriptions/{speaker_xx}'
  return s3.ls(parent_folder)
  """

def get_transcriptions_paths(channel):
  """
  Returns:
  Transcription paths for each video, no speakers
  [
    [
     channel/<video1>/video_data/transcriptions/1.json,
     channel/<video1>/video_data/transcriptions/2.json,
     ],
    [
     channel/<video2>/video_data/transcriptions/1.json,
     channel/<video2>/video_data/transcriptions/2.json,
     ],
     ...
  ]
  """
  video_data_paths = get_video_data_paths(channel)
  transcription_paths = []
  for video_data_path in video_data_paths:
    transcription_paths.append(s3.ls(opj(video_data_path,'transcriptions')))
  return transcription_paths

def get_transcription_paths_video(channel, video):
  return s3.ls(opj(channel,'video_data', video, 'transcriptions'))

def get_transcription_paths_speaker(video_data_path,speaker_xx=""):
  if speaker_xx == "":
    # a problem with this is that it's going to return folders instead of one. I guess this would've need to happen eventually
    parent_folder = f'{video_data_path}transcriptions/{speaker_xx}'
  else:
    parent_folder = f'{video_data_path}transcriptions/{speaker_xx}'
  return s3.ls(parent_folder)

def get_transcription_paths_for_channel(channel):
  """
  I guess this should be....
  []
  
  """
  transcription_paths_for_channel = []
  video_data_paths = get_video_data_paths(channel)
  for video_data_path in video_data_paths:
    print(video_data_path)
    speaker_xx = get_speaker_xx(video_data_path)
    transcription_paths_for_channel.append(get_transcription_paths_speaker(video_data_path,speaker_xx))
  return transcription_paths_for_channel




def s3_transcription_path_to_s3_clip_path(transcription_path):
    """
    Converts an S3 transcription file path to the corresponding clip file path.

    Parameters:
    - transcription_path (str): The S3 path of the transcription file.

    Returns:
    The S3 path of the corresponding clip file.
    """
    # Replace the 'transcriptions' segment with 'clips' and change the file extension from '.json' to '.wav'
    clip_path = transcription_path.replace('/transcriptions/', '/clips/').replace('.json', '.mp4')
    return clip_path

def get_video_data_paths(channel):
  files = s3.ls(f'{channel}/video_data/')
  return files

def get_channel_from_speaker(speaker):
    # Download the JSON content as a bytes object
    json_bytes = s3.download_file_to_memory(f's3://cliptu/speakers_index.json')
    
    # Decode the bytes object to get a string and then parse the string with json.loads()
    speakers_index = json.loads(json_bytes.decode('utf-8'))
    
    # Access the channel using the speaker key
    channel = speakers_index[speaker]
    return channel

def get_speaker_xx(video_data_path):
  json_bytes = s3.download_file_to_memory(f's3://cliptu/{video_data_path}identified_speaker.json')
  #speaker_xx = json.loads(json_bytes.decode('utf-8'))["speaker"]
  speaker_xx = jls(json_bytes.decode('utf-8'))["speaker"]
  return speaker_xx

def file_exists(s3_url):
    """
    Checks if a file exists in S3.

    Parameters:
    - s3_url (str): The full S3 path of the file (e.g., 's3://bucket-name/path/to/file.txt')

    Returns:
    - bool: True if the file exists, False otherwise.
    """
    if not s3_url.startswith("s3://"):
        raise ValueError("URL must be an S3 URL starting with 's3://'")
    
    s3_path = s3_url[5:]
    bucket_name, object_name = s3_path.split('/', 1)

    s3_client = boto3.client('s3')
    
    try:
        s3_client.head_object(Bucket=bucket_name, Key=object_name)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            raise e  # Re-raise the exception if it's not a 404 error


def get_transcription_folder_paths(channel):
    # i.e. s3://cliptu/MrBeast/video_data/＂Beast＂ Channel Trailer-h77pHTSPSiw/transcriptions/
    video_data_paths = ls(f'{channel}/video_data/')
    transcription_folder_paths = opjs(video_data_paths,'transcriptions')
    return transcription_folder_paths

def get_transcriptions_for_a_channel(channel):
    """
    Retrieves transcriptions for all videos in a given channel from S3.

    Parameters:
    - channel (str): The channel to retrieve transcriptions for.

    Returns:
    A list of all transcription file paths for the channel.
    """
    transcription_folder_paths = get_transcription_folder_paths(channel)

    for transcription_folder_path in transcription_folder_paths:
      video_name = f'{transcription_folder_path.split("/")[-2]}'
      print(f'{transcription_folder_path}')
      print(f'{video_name}')
      # I definitely want to fix this - I want to use full s3 paths in s3.py or not. I say not. Assume s3://cliptu/
      transcription_folder_path = f's3://cliptu/{transcription_folder_path}'
      download_folder(transcription_folder_path, f'jobs/{channel}/{video_name}/transcriptions')

def get_transcriptions_for_a_video(channel, video):

    """
    Retrieves all transcriptions for a specific video in a channel from S3.

    Parameters:
    - channel (str): The channel of the video.
    - video (str): The specific video to retrieve the transcriptions for.

    Returns:
    A list of transcription documents or an empty list if none found.
    """
    bucket_name = 'cliptu'
    prefix = f'{channel}/video_data/{video}/transcriptions/'
    print(f"Looking for transcriptions in: s3://{bucket_name}/{prefix}")
    
    transcriptions = []
    
    try:
        transcription_files = list_s3_objects(bucket_name, prefix)
        print(f"Found {len(list(transcription_files))} transcription files")
        for transcript_key in transcription_files:
            if transcript_key.endswith('.json'):
                print(f"Processing transcription file: {transcript_key}")
                response = s3_client.get_object(Bucket=bucket_name, Key=transcript_key)
                transcript = json.loads(response['Body'].read().decode('utf-8'))
                transcriptions.append(transcript)
        
        if not transcriptions:
            print(f"No transcriptions found for video {video} in channel {channel}")
        else:
            print(f"Retrieved {len(transcriptions)} transcriptions for video {video}")
    except ClientError as e:
        print(f"Error retrieving transcriptions for video {video}: {e}")
    
    return transcriptions