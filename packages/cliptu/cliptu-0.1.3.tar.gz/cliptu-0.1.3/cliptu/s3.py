import boto3
import os
import json
from botocore.exceptions import ClientError

from cliptu.s3_utils import *
from cliptu.channel import *
import cliptu.ffprobe as ffprobe
from utils.utils import *

"""
anatomy of an s3 uri
s3://bucket-name/object-key
"""

def has_been_processed(channel, video_name, whisper_x=False, CLIP=False):
  # download the file to local because we'll upload it later
    if download_file(f's3://cliptu/{channel}/processed.json', 'processed.json'):
        processed_json = utils.jl('processed.json')
        if whisper_x:
            # not processed
            if video_name not in processed_json['whisper_x']:
                return False
            # processed
            else:
                return True
        elif CLIP:
            # not processed
            if video_name not in processed_json['CLIP']:
                return False
            # processed
            else:
                return True
    else:
        print(f'processed.json does not exist yet')
        return False


def download_audio(channel, whisper_x=False, CLIP=False):
    """
    Downloads videos from a specific channel to 'jobs/{channel}/videos/, typically to be processed by CLIP or whisper_x.

    Pass in whisper_x=True or CLIP=True to download whisper_x so we know which 'processed.json' dict to check against to skip videos already processed

    returns paths, which are relative, i.e. DOES NOT include 's3://cliptu'

    It's a generator where each iteration:
      * gets a remote file path
      * evaluates if it's already been processed
      * downloads it 
      * filters it based length (right now, over 3.5 hours is it not processed, but added to incomplete.pkl)
    """
    # Get all video paths in the channel
    s3_audio_paths = ls(f's3://cliptu/{channel}/audio/')

    skipped = 0
    processing = 0
    for i, s3_audio_path in enumerate(s3_audio_paths):
        audio_filename = os.path.basename(s3_audio_path)
        # remove the extension
        audio_name = os.path.splitext(audio_filename)[0] # 'The Talk： Kanye West & Elon Musk'

        print(f'skipped: {skipped}, processed: {processing}')
        #  check if video already processed
        if CLIP and has_been_processed(channel, audio_name, CLIP=True):
            print(f'{i} / {len(s3_audio_paths)-1} - {audio_name} already processed by CLIP, skipping', flush=True)
            skipped += 1
        elif whisper_x and has_been_processed(channel, audio_name, whisper_x=True):
            print(f'{i} / {len(s3_audio_paths)-1} - {audio_name} already processed by whisper_x, skipping', flush=True)
            skipped += 1
            continue
        else:
            print(f'{i} / {len(s3_audio_paths)-1} - {audio_filename} not processed', flush=True)
            processing += 1

        # download the audio to local
        local_audio_path = f'jobs/{channel}/audio/{audio_filename}'
        os.makedirs(os.path.dirname(local_audio_path), exist_ok=True)
        download_file(s3_audio_path, local_audio_path)

        # Check if audio should be skipped because it's too long
        """
        duration = ffprobe.get_video_duration(local_audio_path)
        if duration > 3.5 * 3600:
            print(f'{i} / {len(s3_audio_paths)} - {audio_filename} duration is {duration} (greater than the 3.5 hour limit), skipping', flush=True)
            # upload processed.json
            processed_json = utils.jl('processed.json')
            processed_json['whisper_x'][video_name] = ''
            utils.jd(processed_json, 'processed.json')
            upload_file('processed.json', f'{channel}/processed.json')
            continue
        """

        # create paths obj to help caller easily work with channels 
        paths = {}
        paths['s3'] = {}
        paths['audio'] = utils.get_file_basename(local_audio_path)
        paths['channel'] = local_audio_path.split('/')[1]
        paths['audio_data'] = f'{paths["channel"]}/audio_data/'
        paths['audio_data_audio'] = f'{paths["channel"]}/audio_data/{paths["audio"]}'


        # yield full s3 url and utility obj
        yield local_audio_path, paths


def download_videos(s3_client, channel, whisper_x=False, CLIP=False):
    """
    Downloads videos from a specific channel to 'jobs/{channel}/videos/, typically to be processed by CLIP or whisper_x.

    Pass in whisper_x=True or CLIP=True to download whisper_x so we know which 'processed.json' dict to check against to skip videos already processed

    returns paths, which are relative, i.e. DOES NOT include 's3://cliptu'

    It's a generator where each iteration:
      * gets a remote file path
      * evaluates if it's already been processed
      * downloads it 
      * filters it based length (right now, over 3.5 hours is it not processed, but added to incomplete.pkl)
    """
    # Get all video paths in the channel
    s3_video_paths = ls(f's3://cliptu/{channel}/videos/')

    skipped = 0
    processing = 0
    for i, s3_video_path in enumerate(s3_video_paths):
        video_filename = os.path.basename(s3_video_path)
        video_name = video_filename.replace('.mp4','')

        print(f'skipped: {skipped}, processed: {processing}')
        #  check if video already processed
        if CLIP and has_been_processed(channel, video_name, CLIP=True):
            print(f'{i} / {len(s3_video_paths)} - {video_name} already processed by CLIP, skipping', flush=True)
            skipped += 1
        elif whisper_x and has_been_processed(channel, video_name, whisper_x=True):
            print(f'{i} / {len(s3_video_paths)} - {video_name} already processed by whisper_x, skipping', flush=True)
            skipped += 1
            continue
        else:
            print(f'{i} / {len(s3_video_paths)} - {video_filename} not processed', flush=True)
            processing += 1

        # download the video to local
        local_video_path = f'jobs/{channel}/videos/{video_filename}'
        os.makedirs(os.path.dirname(local_video_path), exist_ok=True)
        download_file(s3_video_path, local_video_path)

        # Check if video needs trimming
        duration = ffprobe.get_video_duration(local_video_path)
        if duration > 3.5 * 3600:
            # ffmpeg.trim_video(local_video_path, duration)
            print(f'{i} / {len(s3_video_paths)} - {video_filename} duration is {duration} (greater than the 3.5 hour limit), skipping', flush=True)
            # upload processed.json
            processed_json = utils.jl('processed.json')
            processed_json['whisper_x'][video_name] = ''
            utils.jd(processed_json, 'processed.json')
            upload_file('processed.json', 'MrBeast/processed.json')
            continue

        # create paths obj to help caller easily work with channels 
        paths = {}
        paths['s3'] = {}
        paths['video'] = utils.get_file_basename(local_video_path)
        paths['channel'] = local_video_path.split('/')[1]
        paths['video_data'] = f'{paths["channel"]}/video_data/'
        paths['video_data_video'] = f'{paths["channel"]}/video_data/{paths["video"]}'


        # yield full s3 url and utility obj
        yield local_video_path, paths

def download_file_to_memory(s3_url):
    """
    Downloads an object from S3 into memory.
    Can be a PITA to use, would like to figure that out / clean up this whole file.
    
    Input:
    - s3_url: URL of the S3 object (e.g., 's3://mybucket/myfolder/myfile.txt')
   
    Output: 
    The contents of the S3 object as a bytes object.
    """
    if not s3_url.startswith("s3://"):
        raise ValueError("URL must be an S3 URL starting with 's3://'")
    
    s3_path = s3_url[5:]
    bucket_name, object_name = s3_path.split('/', 1)
    
    # Initialize the S3 client
    s3_client = boto3.client('s3')
    
    # Download the object into memory
    response = s3_client.get_object(Bucket=bucket_name, Key=object_name)
    #return response['Body'].read()
    return response['Body'].read().decode('utf-8')

def download_json_to_memory(s3_url):
  json_bytes = download_file_to_memory(s3_url)
  #return json.loads(json_bytes.decode('utf-8'))
  return json.loads(json_bytes)

def download_file(s3_url, local_file_path):
    """
    Downloads an object from S3 to a local file.
    Does NOT create parent folders, so you must mkdir -p before calling this.
    
    Parameters:
    - s3_url: URL of the S3 object (e.g., 's3://mybucket/myfolder/myfile.txt')
    - local_file_path: Local path to save the file (e.g., '/path/to/myfile.txt')
    """
    try:
        # Parse the S3 URL
        if not s3_url.startswith("s3://"):
            raise ValueError("URL must be an S3 URL starting with 's3://'")

        s3_path = s3_url[5:]
        bucket_name, object_name = s3_path.split('/', 1)

        # Initialize the S3 client
        s3_client = boto3.client('s3')

        # Create parent folders (if there ARE parent folders)
        if os.path.dirname(local_file_path):
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        # Download the file
        s3_client.download_file(bucket_name, object_name, local_file_path)
        return True
    except Exception as e:
        print(f"Failed to download {s3_url} to {local_file_path}: {e}")
        return False

def download_files(s3_urls, local_folder):
    """
    Downloads an object from S3 to a local file.
    
    Parameters:
    - s3_url: URL of the S3 object (e.g., 's3://mybucket/myfolder/myfile.txt')
    - local_file_path: Local path to save the file (e.g., '/path/to/myfile.txt')
    """
    # Parse the S3 URL
    for s3_url in s3_urls:

      print(f'downloading {s3_url}')
      #i.e. s3://cliptu/LexFridman/video_data/1984 by George Orwell ｜ Lex Fridman-7Sk6lTLSZcA/clips/0.mp4
      video_name =  s3_url.split('/')[5] # i.e. lex_fridman#423
      file_name = os.path.basename(s3_url) # i.e. 4.mp4
      local_file_path = opj(local_folder, f'{video_name}_{file_name}')
      #local_file_path = opj(local_folder,os.path.basename(s3_url))
      s3_path = s3_url[5:]
      bucket_name, object_name = s3_path.split('/', 1)
      
      # Initialize the S3 client
      s3_client = boto3.client('s3')
      
      # Download the file
      s3_client.download_file(bucket_name, object_name, local_file_path)

def upload_file(input, output_path, bucket_name='cliptu', from_memory=False):
    """
    Upload a file or data to an S3 bucket. output_path must NOT include s3://cliptu (use 'relative' path)

    :param input: Path to the file to upload, or data in memory if from_memory is True
    :param output_path: S3 path where the file/data should be stored
    :param bucket_name: Bucket to upload to
    :param from_memory: Boolean indicating whether input_data is in-memory data
    """
    try:
        # Create an S3 client
        s3_client = boto3.client('s3')

        if from_memory:
            # Upload the data from memory
            s3_client.put_object(Body=input, Bucket=bucket_name, Key=output_path)
        else:
            # Upload the file from disk
            s3_client.upload_file(input, bucket_name, output_path)

        print(f"Successfully uploaded to s3://{bucket_name}/{output_path}")
    except Exception as e:
        print(f"Upload failed: {e}")

def download_folder(s3_url, local_dir_path):
  """
  Downloads an entire folder from S3 to a local directory, printing each file as it's downloaded.
  
  Parameters:
  - s3_url: URL of the S3 folder (e.g., 's3://mybucket/myfolder/')
  - local_dir_path: Local path to the directory where files will be saved (e.g., '/path/to/local/dir')

  Example:
  s3.download_folder('s3://cliptu/twitch', 'test_download_folder')
  """
  # Parse the S3 URL
  if not s3_url.startswith("s3://"):
    raise ValueError("URL must be an S3 URL starting with 's3://'")
  
  s3_path = s3_url[5:]
  bucket_name, prefix = s3_path.split('/', 1)
  
  # Ensure the prefix ends with a '/'
  if not prefix.endswith('/'):
    prefix += '/'

  # Initialize the S3 client
  s3_client = boto3.client('s3')
  
  # List and download all files in the folder
  paginator = s3_client.get_paginator('list_objects_v2')
  for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
    for obj in page.get('Contents', []):
      # Get the path relative to the prefix
      relative_path = obj['Key'][len(prefix):]
      # Construct the local file path
      local_file_path = os.path.join(local_dir_path, relative_path)
      
      # Ensure the local directory exists
      os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
      
      # Download the file
      print(f"Downloading: {relative_path}")  # Print the file being downloaded
      s3_client.download_file(bucket_name, obj['Key'], local_file_path)

def upload_folder(input_folder, output_folder, bucket_name='cliptu'):
  """
  Uploads an entire folder from a local directory to an S3 bucket, printing each file as it's uploaded.

  Parameters:
  - input_folder: Local path to the folder to be uploaded (e.g., '/path/to/local/dir')
  - output_folder: S3 folder path where files will be saved (e.g., 'myfolder/')
  - bucket_name: Name of the S3 bucket (default: 'cliptu')

  Example:
  s3.upload_folder('test_upload_folder', 'twitch')
  """
  # Ensure the output folder ends with a '/'
  if not output_folder.endswith('/'):
    output_folder += '/'

  # Initialize the S3 client
  s3_client = boto3.client('s3')
  
  # Walk through the local directory and upload files
  for root, _, files in os.walk(input_folder):
    for file_name in files:
      # Construct the full local path
      local_file_path = os.path.join(root, file_name)
      # Determine the S3 key based on the output folder
      relative_path = os.path.relpath(local_file_path, input_folder)
      s3_key = f"{output_folder}{relative_path.replace(os.sep, '/')}"
      
      # Upload the file
      print(f"Uploading: {relative_path}", flush=True)  # Print the file being uploaded
      s3_client.upload_file(local_file_path, bucket_name, s3_key)

def rm(s3_url):
  """
  Removes an entire folder from S3, deleting all files under the specified prefix.

  Parameters:
  - s3_url: URL of the S3 folder to be deleted (e.g., 's3://mybucket/myfolder/')

  Example:
  s3.remove_folder('s3://cliptu/twitch')
  """
  # Parse the S3 URL
  if not s3_url.startswith("s3://"):
    raise ValueError("URL must be an S3 URL starting with 's3://'")

  s3_path = s3_url[5:]
  bucket_name, prefix = s3_path.split('/', 1)

  # Ensure the prefix ends with a '/'
  if not prefix.endswith('/'):
    prefix += '/'

  # Initialize the S3 client
  s3_client = boto3.client('s3')

  # List all objects under the prefix and delete them
  paginator = s3_client.get_paginator('list_objects_v2')
  objects_to_delete = []

  for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
    objects_to_delete.extend([{'Key': obj['Key']} for obj in page.get('Contents', [])])

  if objects_to_delete:
    print(f"Deleting {len(objects_to_delete)} files from {s3_url}")
    s3_client.delete_objects(Bucket=bucket_name, Delete={'Objects': objects_to_delete})
  else:
    print(f"No files found at {s3_url}")


def ls(s3_path):
    """
    Lists full paths of directories and files in a specified path within an S3 bucket.
    Requires full S3 path (s3://<bucket>/path/to/folder).

    Parameters:
    - s3_path (str): The full S3 path to list contents from (e.g., 's3://mybucket/myfolder/subfolder/').

    Returns:
    A list of full S3 paths for directories and files.
    """
    if not s3_path.startswith('s3://'):
        raise ValueError("s3_path must start with 's3://'")

    # Split the s3_path into bucket and prefix
    parts = s3_path[5:].split('/', 1)
    bucket_name = parts[0]
    s3_path_prefix = parts[1] if len(parts) > 1 else ''

    s3_client = boto3.client('s3')
    paginator = s3_client.get_paginator('list_objects_v2')

    results = []

    # Ensure the prefix ends with a slash if it's not empty and does not already end with one
    if s3_path_prefix and not s3_path_prefix.endswith('/'):
        s3_path_prefix += '/'

    # Use the paginator to handle buckets with many objects
    for page in paginator.paginate(Bucket=bucket_name, Prefix=s3_path_prefix, Delimiter='/'):
        # CommonPrefixes contains directories under the prefix
        for prefix in page.get('CommonPrefixes', []):
            results.append(f"s3://{bucket_name}/{prefix['Prefix']}")
        # Contents contains files under the prefix
        for obj in page.get('Contents', []):
            results.append(f"s3://{bucket_name}/{obj['Key']}")

    return results

def list_s3_objects(bucket_name, prefix):
    """
    Lists objects in an S3 bucket with the given prefix - folders and files. Unsure if full paths or just last part.

    Parameters:
    - bucket_name (str): The name of the S3 bucket.
    - prefix (str): The prefix to filter objects by.

    Yields:
    S3 object keys matching the prefix.
    """
    paginator = s3_client.get_paginator('list_objects_v2')
    
    try:
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            for obj in page.get('Contents', []):
                yield obj['Key']
    except ClientError as e:
        print(f"Error listing S3 objects: {e}")