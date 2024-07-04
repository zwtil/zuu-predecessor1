from dataclasses import dataclass, field
import typing
import pyscreeze
from zrcl.beta_desktop_automation.region_marker import RegionMarker
from zrcl.ext_easyocr import get_text_coords
import pyautogui

@dataclass
class FeatureCropper:
    """
    Base class for cropping screenshots and target matching
    """
    targetMatch : typing.Union[str, typing.Callable]
    regionMarker: RegionMarker
    recognitionParams: dict = field(default_factory=dict)
    desktopAutomationStep : typing.Callable = lambda x, y : pyautogui.click(x, y)
    _lastResults = None
    _lastScreenshot = None
    _lastMatches = None
    _lastMatch = None
    _lastResult = None

    def _preprocessing(self):
        """
        Preprocessing step for cropping
        """
        pass

    def _crop(self):
        """
        Crop the screenshot
        """
        pass

    def _crop_postprocessing(self, results):
        """
        Postprocessing step for cropping
        """
        pass

    def _target_match(self, results):
        """
        Match the results with the target
        """
        if not isinstance(results, list):
            results = [results]
        
        if isinstance(self.targetMatch, str):
            def targetMatchFunc(result):
                """
                Evaluate the target match string
                """
                evaluated = eval(self.targetMatch, {"result": result, "self": self})
                return evaluated
        else:
            targetMatchFunc = self.targetMatch

        aggResults = [result for result in results if targetMatchFunc(result)]
        self._lastMatches = aggResults
        return aggResults            

    def _target_parse(self, results):
        """
        Parse the results and return the target
        """
        pass

    def __call__(self):
        """
        Call the feature cropper
        """
        self._preprocessing()
        results = self._crop()
        self._crop_postprocessing(results)
        return self._target_parse(results)
        
@dataclass
class ClosestOcr(FeatureCropper):
    """
    Class for cropping screenshots and matching the closest OCR result
    """
    confidence : float = 0.6 

    def __post_init__(self):
        """
        Post initialization step
        """
        if isinstance(self.targetMatch, str):
            self.targetMatch = f"result[3] == '{self.targetMatch}'"

    def _crop(self):
        """
        Crop the screenshot
        """
        screenshot = self.regionMarker.screenshot
        self._lastScreenshot = screenshot
        results = get_text_coords(screenshot, **self.recognitionParams)
        # confidence filter
        results = [result for result in results if result[2] >= self.confidence]

        self._lastResults = results
        return results

    def _target_parse(self, results):
        """
        Parse the results and return the closest OCR match
        """
        matched = self._target_match(results)
        # get closest match
        closest_match = max(matched, key=lambda result: result[2])
        self._lastMatch = closest_match

        top_left, _, bottom_right, _ = closest_match[0]
        center_x = (top_left[0] + bottom_right[0]) / 2
        center_y = (top_left[1] + bottom_right[1]) / 2

        self._lastResult = (center_x, center_y)
        return center_x, center_y

@dataclass
class ImageMatcher(FeatureCropper):
    """
    Class for cropping screenshots and matching an image
    #TODO action not specified
    """
    targetImage: typing.Union[str, typing.Any] = None
    confidence: float = 0.6
    matchAlgorithm: str = 'auto'  # Assume 'auto' or could be specific like 'cv2'

    def __post_init__(self):
        """
        Post initialization step
        """
        super().__post_init__() 
        if isinstance(self.targetMatch, str):
            self.targetMatch = f"result['confidence'] >= {self.confidence} and {self.targetMatch}"

    def _crop(self):
        """
        Crop the screenshot
        """
        screenshot = self.regionMarker.screenshot
        self._lastScreenshot = screenshot
        results = pyscreeze.locate(self.targetImage, screenshot, confidence=self.confidence, algo=self.matchAlgorithm)
        if results:
            self._lastResults = results
        return results

    def _target_parse(self, results):
        """
        Parse the results and return the image match
        """
        if results:
            box = pyscreeze.Box(results)  # assuming Box is a valid type from pyscreeze that handles rectangles
            center_x = (box.left + box.width / 2)
            center_y = (box.top + box.height / 2)
            self._lastMatch = box
            self._lastResult = (center_x, center_y)
            return center_x, center_y
        return None
