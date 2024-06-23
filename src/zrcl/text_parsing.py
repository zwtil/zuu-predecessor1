import base64
from PIL import Image
import io


def load_base64_img(string: str):
    """
    Load an image from a base64 encoded string.

    Args:
        string (str): The base64 encoded string representing the image.

    Returns:
        Image: The loaded image object.

    This function takes a base64 encoded string as input and loads an image from it. It checks if the string starts with
    "data:image/png;base64," and removes that prefix if it exists. Then, it decodes the base64 string using the
    `base64.b64decode` function and creates an in-memory bytes object using `io.BytesIO`. Finally, it uses the
    `Image.open` function from the Pillow library to open the image from the bytes object and returns the loaded image.
    """

    if string.startswith("data:image/png;base64,"):
        string = string[22:]
    return Image.open(io.BytesIO(base64.b64decode(string)))
