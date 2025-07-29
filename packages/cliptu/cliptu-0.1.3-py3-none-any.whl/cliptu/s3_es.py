
import cliptu.s3_path as s3_path
from cliptu.ffmpeg import *
from cliptu.s3_path import *

def create_document_with_metadata(json_content, s3_path, channel, speaker):
    """
    Enhances the transcript JSON with additional metadata for tracing back to its source.

    Parameters:
    - json_content (bytes): The raw JSON content from the S3 file.
    - s3_path (str): The S3 path from where the file was downloaded.

    Returns:
    A dictionary representing the enhanced document.
    """
    # get video and speaker from path
    video_name = s3_path.split('/')[5]
    speaker = s3_path.split('/')[-2]


    #json_content = {k: v for k, v in json_content.items() if k == 'text'}
    
    json_content['video_name'] = video_name
    json_content['s3_path'] = s3_path
    json_content['clip_path'] = s3_transcription_path_to_s3_clip_path(s3_path)
    json_content['channel'] = channel
    json_content['speaker'] = speaker
    # use 
    # json_content['start'] = start
    # json_content['end'] = end


    return json_content

def upload_transcriptions_folder(es, input_folder, es_index, channel, speaker=None):
  """
  Transfer transcription from s3 input folder to es index
  This must expect a list of jsons, i.e.
  [*1.json,*2.json]
  """
  for i,json_path in enumerate(input_folder):
    s3_path = 's3://cliptu/' + json_path
    json_content = s3.download_json_to_memory(s3_path)
    document = create_document_with_metadata(json_content, s3_path, channel, speaker)
    es.index(index=es_index, body=document)

def upload_transcriptions_channel(es, channel):
  """
  for a channel, get all transcriptions from s3, upload to es.
  """
  transcription_paths = s3_path.get_transcriptions_paths(channel)
  for transcriptions_folder in transcription_paths:
    es_index = 'transcriptions'
    upload_transcriptions_folder(es, transcriptions_folder, es_index, channel, "")

def upload_transcriptions_video(es, channel, video_name):
  transcription_paths = s3_path.get_transcription_paths_video( channel, video_name)
  upload_transcriptions_folder(es, transcription_paths, 'transcriptions', channel, "")