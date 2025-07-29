from utils.utils import *
import os
import shlex

def extract_clip(input_path, output_path, start_time=None, end_time=None, gpu=False):
    """
    Extracts a clip from a video using ffmpeg with optional start and end times.

    For more notes see backend/test/extract_clip/README.md

    We really don't like building the string like this, it's not clear what's being executed.
    """
    # Quote paths for safety
    input_path = shlex.quote(input_path)
    output_path = shlex.quote(output_path)
    
    # Start building the base ffmpeg command
    if gpu:
        cmd = f"ffmpeg -y -loglevel error -hwaccel cuda"
    else:
        cmd = f"ffmpeg -y -loglevel error"
    
    # Add the start time if provided
    if start_time:
        cmd += f" -ss {start_time}"
    
    # Add the input file
    cmd += f" -i {input_path}"
    
    # Add the end time if provided
    # omitting end_time might be broken after adding end_time - start_time
    if end_time:
        cmd += f" -to {end_time - start_time}"
    
    # Complete the command with the copy and output options
    cmd += f" -c copy {output_path}"
    
    # Print the command and execute it
    print('----------------------------------')
    print(cmd)
    print('----------------------------------')

    os.makedirs(os.path.dirname(output_path.strip("'")), exist_ok=True)
    os.system(cmd)
    
    return cmd

def extract_clips_global_timestamps_segment(segmentation, input_video, output_folder):
    """
    so this should write to clips and without clip_
    """
    """
    return / write: 
    - Extracts clips from an input video based on diarization results and writes them to a common folder.

    - writes a JSON file mapping each clip to its global timestamp and speaker.
    
    Parameters:
    - diarization.pkl: A pyannote.core.annotation.Annotation object containing diarization results.
    - input_video: Path to the input video file.
    - output_folder: Path to the folder where extracted clips and mapping file will be saved.
    """
    clips_folder = os.path.join(output_folder, 'clips')
    os.makedirs(clips_folder, exist_ok=True)
    
    clips_mapping = []
    for i, seg in enumerate(segmentation.get_timeline()):
        output_clip_path = os.path.join(clips_folder, f'{i}.mp4')
        extract_clip(input_video, output_clip_path, start_time=seg.start, end_time=(seg.end - seg.start))
        clips_mapping.append({
            'clip_path': output_clip_path,
            'start': seg.start,
            'end': seg.end,
        })
    
    mapping_file_path = os.path.join(output_folder, 'clips_mapping.json')
    with open(mapping_file_path, 'w') as f:
        json.dump(clips_mapping, f, indent=2)

    return clips_folder

def extract_clips_global_timestamps(diarization, input_video, output_folder):
    """
    so this should write to clips and without clip_
    """
    """
    return / write: 
    - Extracts clips from an input video based on diarization results and writes them to a common folder.

    - writes a JSON file mapping each clip to its global timestamp and speaker.
    
    Parameters:
    - diarization.pkl: A pyannote.core.annotation.Annotation object containing diarization results.
    - input_video: Path to the input video file.
    - output_folder: Path to the folder where extracted clips and mapping file will be saved.
    """
    clips_folder = os.path.join(output_folder, 'clips')
    os.makedirs(clips_folder, exist_ok=True)
    
    clips_mapping = []
    for i, (seg, track, label) in enumerate(diarization.itertracks(yield_label=True)):
        output_clip_path = os.path.join(clips_folder, f'{i}.mp4')
        extract_clip(input_video, seg.start, seg.end, output_clip_path)
        clips_mapping.append({
            'clip_path': output_clip_path,
            'start': seg.start,
            'end': seg.end,
            'speaker': label
        })
    
    mapping_file_path = os.path.join(output_folder, 'clips_mapping.json')
    with open(mapping_file_path, 'w') as f:
        json.dump(clips_mapping, f, indent=2)

    return clips_folder


def preprocess_clip(clip_path, output_dir):
    """
    Currently used in /concatenate_clips
    Takes clips sent from front_end and stored in temp
    and 'preprocesses' them and outputs them to preprocessed

    really, specifies audio and video codecs, bitrate, resolution, etc.

    reminder: codecs are within a container where mp4 is a container.
    """
    output_file_name = os.path.basename(clip_path)
    output_path = os.path.join(output_dir, output_file_name)
    clip_path_shlex = shlex.quote(clip_path)
    output_path_shlex = shlex.quote(output_path)
    print('preprocess_clip')
    #ffmpeg_command = f"ffmpeg -y -hide_banner -loglevel error -hwaccel cuda -i {clip_path_shlex} -c:v libx264 -preset superfast -c:a aac -strict experimental -b:a 192k -r 30 -s 1280x720 {output_path_shlex}"

    ffmpeg_command = f"ffmpeg -y -hide_banner -loglevel error -hwaccel cuda -i {clip_path_shlex} -c:v libx264 -c:a aac -strict experimental -b:a 192k -r 30 -s 1920x1080 {output_path_shlex}"
    os.system(ffmpeg_command)
    return output_path

def concatenate_clips(clip_folder, file_name, sort=True, rm=True):
    """
    Concatenates local clips

    This is coupled to the cliptu clip naming scheme, i.e.
    Nevada Rally with Vice President Kamala Harris and Governor Tim Walz-fDcXZp4Vi4Y/clips/120.mp4
    hmmmmm actually maybe it's the cloudfront urls...because there's no underscore in this url
    let's add a switch for sort so we can use it outside pipeline
    """
    clip_paths = ld(clip_folder)

    # Sorting by video name and then by the numeric suffix in the filename
    if sort:
        clip_paths.sort(key=lambda x: (
            x.rsplit('_', 1)[0],  # This gives everything before the last '_'
            int(x.rsplit('_', 1)[1].split('.')[0])  # This extracts the number between the last '_' and '.'
        ))

    # Directory to store preprocessed clips
    preprocessed_dir = 'preprocessed_clips'
    os.makedirs(preprocessed_dir, exist_ok=True)

    # Preprocess clips and create the file list for concatenation
    list_file_path = 'concat_list.txt'
    with open(list_file_path, 'w') as list_file:
        print('Preprocessing clips')
        for i,clip_path in enumerate(clip_paths):
            print(f'preprocessing clip {i}/{len(clip_paths)}')
            preprocessed_path = preprocess_clip(opj(clip_folder,clip_path), preprocessed_dir)
            preprocessed_path_replaced = preprocessed_path.replace("'", "'\\''")
            #preprocessed_path_escaped = shlex.quote(preprocessed_path)
            list_file.write(f"file '{preprocessed_path_replaced}'\n")
    # Concatenate using ffmpeg
    list_file_path_escaped=shlex.quote(list_file_path)
    file_name_escaped=shlex.quote(file_name)
    print('concatenate_clips')
    concat_command = f"ffmpeg -y -hide_banner -loglevel error -f concat -safe 0 -i {list_file_path_escaped} -c copy {file_name_escaped}"
    os.system(concat_command)
    # not sure why concat_list.txt doesn't exist at this point.. get's deleted somewhere?
    if rm:
        rm(list_file_path)
        rm(clip_folder)
    return file_name

def extract_clips_speaker(speaker, diarization, input_video, output_folder):
    """
    Extracts clips for a specific speaker from an input video based on diarization results.
    
    Parameters:
    - speaker: The target speaker identifier (e.g., "speaker_xx").
    - diarization: A pyannote.core.annotation.Annotation object containing diarization results.
    - input_video: Path to the input video file.
    - output_folder: Path to the folder where extracted clips will be saved.
    
    Returns:
    - The path to the output folder where clips are saved.
    """
    mkdir(output_folder)
    for i, (seg, track, label) in enumerate(diarization.itertracks(yield_label=True)):
        if label == speaker:
            output_clip_path = f'{output_folder}/{i}.mp4'
            extract_clip(input_video, seg.start, seg.end, output_clip_path)
    return output_folder

def extract_clips_all_speakers(diarization, input_video, output_folder):
    """
    Extracts clips for a specific speaker from an input video based on diarization results.
    
    Parameters:
    - diarization: A pyannote.core.annotation.Annotation object containing diarization results.
    - input_video: Path to the input video file.
    - output_folder: Path to the folder where extracted clips will be saved.
    
    Returns:
    - The path to the output folder where clips are saved. Clips are stored in a folder for each speaker.
    """

    speakers = set()
    for i, (seg, track, label) in enumerate(diarization.itertracks(yield_label=True)):
      speakers.add(label)
    
    output_folder = opj(output_folder,'clips')

    for speaker in speakers:
      mkdir(opj(output_folder,speaker))

    clip_paths =[]
    for i, (seg, track, label) in enumerate(diarization.itertracks(yield_label=True)):
        output_clip_path = f'{output_folder}/{label}/{i}.mp4'
        extract_clip(input_video, seg.start, seg.end, output_clip_path)
        clip_paths.append(d(output_clip_path))
    return clip_paths

def extract_clips(diarization,input_video, output_folder):
  for i, (seg, track, label) in enumerate(diarization.itertracks(yield_label=True)):
    output_clip_path = f'{output_folder}/{i}.mp4'
    extract_clip(input_video, seg['start'], seg['end'], output_clip_path)
  return output_folder