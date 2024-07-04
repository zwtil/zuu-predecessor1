import typing
import io
import numpy
import easyocr


def get_text_coords(
    image: typing.Union[str, bytes, numpy.ndarray, io.BytesIO],
    lang: typing.List[str] = ["en"],
    additionalReaderArgs: typing.Dict = {},
):
    """
    Extracts the coordinates of text in an image using the EasyOCR library.

    Args:
        image (typing.Union[str, bytes, numpy.ndarray, io.BytesIO]): The input image. It can be a file path, bytes,
            numpy array, or an io.BytesIO object.
        lang (typing.List[str], optional): The list of languages to recognize. Defaults to ["en"].
        additionalReaderArgs (typing.Dict, optional): Additional arguments to pass to the EasyOCR reader.
            Defaults to {}.

    Returns:
        List[Tuple[Tuple[int, int], Tuple[int, int], float, str]]: A list of tuples containing the coordinates of the
            detected text in the image. Each tuple contains the bottom left and top right coordinates of the text, the
            confidence level, and the recognized text.

    Raises:
        None

    Example:
        >>> image_path = "path/to/image.jpg"
        >>> coords = get_text_coords(image_path)
        >>> print(coords)
        [(bottom_left_coords, top_right_coords, confidence, text), ...]
    """
    reader = easyocr.Reader(lang_list=lang)

    if isinstance(image, io.BytesIO):
        image = numpy.array(image)

    result = reader.readtext(image, **additionalReaderArgs)
    coordinates = []
    for detection in result:
        bottom_left = detection[0][0]
        top_right = detection[0][2]
        confidence = detection[1]
        text = detection[2]
        coordinates.append((bottom_left, top_right, confidence, text))

    return coordinates


def get_paragraph_coords(
    image: typing.Union[str, bytes, numpy.ndarray, io.BytesIO],
    lang: typing.List[str] = ["en"],
    additionalReaderArgs: typing.Dict = {},
):
    """
    Extracts the coordinates of paragraphs in an image using the EasyOCR library.

    Args:
        image (typing.Union[str, bytes, numpy.ndarray, io.BytesIO]): The input image. It can be a file path, bytes,
            numpy array, or an io.BytesIO object.
        lang (typing.List[str], optional): The list of languages to recognize. Defaults to ["en"].
        additionalReaderArgs (typing.Dict, optional): Additional arguments to pass to the EasyOCR reader.
            Defaults to {}.

    Returns:
        List[Tuple[Tuple[int, int], Tuple[int, int], float, str]]: A list of tuples containing the coordinates of the
            detected paragraphs in the image. Each tuple contains the bottom left and top right coordinates of the
            paragraph, the confidence level, and the recognized text.

    Raises:
        None

    Example:
        >>> image_path = "path/to/image.jpg"
        >>> coords = get_paragraph_coords(image_path)
        >>> print(coords)
        [(bottom_left_coords, top_right_coords, confidence, text), ...]
    """
    if "paragraph" not in additionalReaderArgs:
        additionalReaderArgs["paragraph"] = True

    return get_text_coords(image, lang, additionalReaderArgs)
