from glob import glob
from utils.utils import *

def create_transcription_paths_to_transcriptions(transcriptions_path, video_data_path):
  """
  Creates a dictionary mapping transcription paths to their transcriptions and writes it to a JSON file.

  Args:
  clip_paths (list): List of clip file paths.
  transcriptions_dir (str): Directory containing the transcription files.

  Returns:
  None
  """
  mapping = {}
  for transcription_path in glob(f'{transcriptions_path}/*.json'):
    with open(transcription_path, 'r') as f:
      transcription = json.load(f)['text']
    mapping[transcription_path.split('/')[-1]] = transcription
  print(mapping)
  with open(f'{video_data_path}/transcription_paths_to_transcriptions.json', 'w') as f:
    json.dump(mapping, f)
  return mapping


def write_transcription(segments, output_path):
  all_text = ""  # To hold all concatenated text
  all_segments = []  # To hold all segment objects or dicts

  for segment in segments:
      all_text += segment.text + " " 
      all_segments.append({
          'start': segment.start,
          'end': segment.end,
          'text': segment.text
      })

  faster_whisper_json = {'segments': all_segments, 'text': all_text}

  # Save the transcription results to a JSON file
  with open(output_path, 'w') as f:
      json.dump(faster_whisper_json, f)

def transcribe_folder_faster(input_folder, output_folder, model):
    """
    Transcribe all audio files in the input_folder and save the transcriptions in the output_folder.
    """
    # Create the output directory if it doesn't exist
    mkdir(output_folder)
    for clip_path in glob(f'{input_folder}/*.mp4'):  # Assuming you're working with .wav files; adjust as necessary
        transcription_json_path = opj(output_folder,f'{get_file_basename(clip_path)}.json')
        transcribe_faster(clip_path, transcription_json_path, model)

def transcribe_faster(input_path, output_path, model):
    """
    Transcribe a single audio file and save the transcription to a JSON file.

    Args:
        input_path (str): Path to the audio file.
        output_path (str): Path to save the JSON file.
        model (object): Transcription model object.
    """
    try:
        segments, info = model.transcribe(input_path, language='en', beam_size=5)
        write_transcription(segments, output_path)
        print(f'transcribe: {output_path}', flush=True)

    except Exception as e:
        print(f"An error occurred during the transcription of {input_path}\n{str(e)}")
