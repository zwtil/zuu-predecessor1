import pyscreeze


class PyscreezeImports:
    from pyscreeze import (  # noqa: E402
        center as center,
        locateAll as locateAll,
        locateAllOnScreen as locateAllOnScreen,
        locateCenterOnScreen as locateCenterOnScreen,
        locateOnScreen as locateOnScreen,
        locateOnWindow as locateOnWindow,
        pixel as pixel,
        pixelMatchesColor as pixelMatchesColor,
        screenshot as screenshot,
    )


def boxcenter(box):
    """
    Calculate the center coordinates of the given box.

    Parameters:
        box : tuple or Box
            The input box for which to calculate the center coordinates.

    Returns:
        Point
            The center coordinates of the box as a Point object.
    """
    if isinstance(box, tuple):
        return pyscreeze.center(box)
    return pyscreeze.Point(box.left + box.width / 2, box.top + box.height / 2)


try:
    pyscreeze._locateAll_opencv

    def locateAllOpenCV(
        needleImage,
        haystackImage,
        grayscale=None,
        limit=None,
        region=None,
        step=1,
        confidence=None,
    ):
        return pyscreeze._locateAll_opencv(needleImage, haystackImage, grayscale, limit, region, step, confidence)  # type: ignore

except AttributeError:
    locateAllOpenCV = None  # type: ignore


try:
    pyscreeze._locateAll_pillow

    def locateAllPillow(
        needleImage,
        haystackImage,
        grayscale=None,
        limit=None,
        region=None,
        step=1,
        confidence=None,
    ):
        return pyscreeze._locateAll_pillow(needleImage, haystackImage, grayscale, limit, region, step, confidence)  # type: ignore

except AttributeError:
    locateAllPillow = None  # type: ignore
