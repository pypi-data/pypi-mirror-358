import cv2
import subprocess
from happy_utils.happy_utils import w, save_image

def get_frame(video_path, timestamp: float, save_path=None):
    """
    Retrieves a single frame from a video at the specified timestamp.

    Parameters:
      video_path (str): Path to the video file.
      timestamp (float): Timestamp in seconds at which to extract the frame.

    Returns:
      numpy.ndarray or None: The frame at the specified timestamp, or None if the frame cannot be read.
    """
    cap = cv2.VideoCapture(video_path)  # Open the video file
    # Set the position in the video (in milliseconds)
    cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
    ret, frame = cap.read()  # Read the frame at the given timestamp
    if save_path:
      save_image(frame, save_path)
    cap.release()  # Release the video capture object
    return frame if ret else None

def reframe(frame, x, y, width, height):
    """
    Extracts a region of interest from an image.

    Parameters:
      frame: The input image (numpy array).
      x, y: The top-left corner coordinates of the region.
      width, height: The width and height of the region.

    Returns:
      The ROI as: img[y:y+height, x:x+width]
    """
    return frame[y:y+height, x:x+width]

def draw_rect(img, x1, y1, width, height, color=(0, 255, 0), thickness=2, save_path=None):
    """
    Draws a rectangle on the image 'img' using the top-left corner (x1, y1)
    and the given width and height.

    Parameters:
      img: The image (numpy array).
      x1, y1: Coordinates of the top-left corner of the rectangle.
      width: The width of the rectangle.
      height: The height of the rectangle.
      color: The rectangle color in BGR (default green).
      thickness: The thickness of the rectangle border.

    Returns:
      The image with the rectangle drawn.
    """
    # Calculate bottom-right corner
    x2 = x1 + width
    y2 = y1 + height
    cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
    if save_path:
       cv2.imwrite(save_path ,img)
    return img

def get_fps(video_path):
  """
  Get the frames per second (FPS) of a video.

  Args:
      video_path (str): Path to the video file.

  Returns:
      float: FPS of the video.
  """
  cap = cv2.VideoCapture(video_path)  # Open video capture
  fps = cap.get(cv2.CAP_PROP_FPS)  # Retrieve the FPS
  cap.release()  # Release the video capture object
  return fps

def get_frames(video_path, timestamps=None, yield_timestamps=False):
    """
    Generator to yield frames from a video.
    
    Args:
        video_path (str): Path to the video file.
        timestamps (list of float, optional): Do not go over the whole video, just get the frames for the timestamps (in seconds).
            If provided, yields a tuple (timestamp, numpy.ndarray) for each timestamp.
            Otherwise, yields all frames sequentially.
        yield_timestamps (bool, optional): If True and timestamps is None,
            calculates and yields the timestamp (using FPS and frame index) along with the frame.
    
    Yields:
        If timestamps is provided or yield_timestamps is True:
            (timestamp, numpy.ndarray) tuples.
        Otherwise:
            numpy.ndarray frames.
    """
    cap = cv2.VideoCapture(video_path)

    # Check if the video was opened successfully
    if not cap.isOpened():
        raise ValueError(f"Error: Cannot open video at path '{video_path}'")
    
    if timestamps is None:
        # DO go through the whole video
        if yield_timestamps:
            # yield timestamps
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_index = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                timestamp = frame_index / fps  # Calculate timestamp from frame index and fps
                yield timestamp, frame
                frame_index += 1
        else:
            # do not yield timestamps (simpler interface)
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                yield frame
    else:
        # DO NOT go through the whole video, only the provided timestamps
        for t in sorted(timestamps):
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
            ret, frame = cap.read()
            if ret:
                yield t, frame
            else:
                print(f"Warning: Could not retrieve frame at {t} seconds.")
    
    cap.release()

def ffprobe(video_file, output_file=""):
  ffprobe_command = [
      'ffprobe', '-v', 'error', '-show_streams', '-show_format', video_file
  ]
  result = subprocess.run(ffprobe_command, capture_output=True, text=True)

  # Prepare to filter ffprobe output
  filtered_lines = []
  for line in result.stdout.split('\n'):
      if 'codec_name=' in line or 'width=' in line or 'height=' in line:
          filtered_lines.append(line)
  filtered_lines = '\n'.join(filtered_lines)
  if output_file:
     w(filtered_lines, output_file)
  print(filtered_lines)
