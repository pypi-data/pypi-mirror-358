from utils import utils as utils

def transcription_file_names_to_s3_uris(channel,video_name, transcription_file_names):
  s3_uris = []
  for transcription_file_name in transcription_file_names:
    s3_uri = f's3://cliptu/{channel}/video_data/{video_name}/transcriptions/{transcription_file_name}'
    s3_uris.append(s3_uri)
  return s3_uris

def transform_json_transcription_file_names_to_s3_uris(channel, video_name, res):
  """
  replace s3 transcription file names with full s3 uris
  """
  for k in res['results'].keys():
    transcription_file_names = res['results'][k]
    s3_uris = []
    for transcription_file_name in transcription_file_names:
      s3_uri = f's3://cliptu/{channel}/video_data/{video_name}/transcriptions/{transcription_file_name}'
      s3_uris.append(s3_uri)
    res['results'][k] = s3_uris

  return res

if __name__ == "__main__":
  channel = "test"
  video_name = "Campaign Event in Raleigh, North Carolina with Vice President Kamala Harris-IbhXnF2Jo94"
  transcription_paths = ["0.json", "1.json"]
  res = utils.jl('response.json')
  for k in res['results'].keys():
    transcription_paths = res['results'][k]
    long_paths = transcription_file_names_to_s3_uris(channel, video_name, transcription_paths)
    res['results'][k] = long_paths
