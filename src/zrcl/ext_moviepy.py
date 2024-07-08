import os
from PIL import Image
from zrcl.ext_pillow import is_mono_color
from zrcl.ext_random import weighted_choice


def make_thumbnail(video_path: str, sec: int = None, avoid_single_color: bool = True):
    """
    Generate a thumbnail image from a video file.

    Args:
        video_path (str): The path to the video file.
        sec (int, optional): The timestamp in seconds at which to generate the thumbnail. If not provided, a random timestamp will be chosen.
        avoid_single_color (bool, optional): Whether to avoid generating thumbnails with a single color. Defaults to True.

    Returns:
        Image: The generated thumbnail image.

    Raises:
        None

    Notes:
        - This function uses the `moviepy` library to generate the thumbnail image.
        - The `sec` argument is used to specify the timestamp at which to generate the thumbnail. If not provided, a random timestamp will be chosen.
        - The `avoid_single_color` argument determines whether to avoid generating thumbnails with a single color. If set to True, the function will keep generating thumbnails until a non-single-color image is found.
        - The function returns an `Image` object representing the generated thumbnail.
    """
    from moviepy.editor import VideoFileClip

    sec = weighted_choice(sumk=2)
    while True:
        clip = VideoFileClip(video_path)

        sec = weighted_choice(sumk=2) + sec

        sec = min(sec, clip.duration)
        frame = clip.get_frame(sec)

        image = Image.fromarray(frame)

        if not avoid_single_color:
            break

        if not is_mono_color(image):
            break

    return image


def thumbnail_folder(
    path: str,
    sec: int = None,
    supported_formats=[".mp4", ".mkv", ".mov", ".avi", ".webm"],
):
    """
    Generates a thumbnail for each file in the specified folder.

    Args:
        path (str): The path to the folder containing the files.
        sec (int, optional): The second at which the thumbnail should be generated. Defaults to None.
        supported_formats (list[str], optional): The list of supported file formats. Defaults to [".mp4", ".mkv", ".mov", ".avi", ".webm"].

    Yields:
        PIL.Image.Image: The thumbnail image.

    """
    for file in os.listdir(path):
        if os.path.splitext(file)[1] in supported_formats:
            yield make_thumbnail(os.path.join(path, file), sec), os.path.join(path, file)

