from PIL import Image


def is_mono_color(image: Image.Image):
    """
    A function to check if all pixels in the image have the same color as the first pixel.

    Parameters:
        image: The image to check for mono-color.

    Returns:
        True if all pixels are the same color, False otherwise.
    """
    first_pixel = image.getpixel((0, 0))

    # Check if all pixels are the same as the first pixel
    for x in range(image.width):
        for y in range(image.height):
            if image.getpixel((x, y)) != first_pixel:
                return False
    return True
