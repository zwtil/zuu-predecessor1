import copy
from dataclasses import dataclass, field
from typing import Optional
import pygetwindow as gw
from PIL import ImageGrab

from zrcl.ext_pygetwindow import get_window_pos
from zrcl.ext_screeninfo import get_monitor_bounds


@dataclass
class RegionSpec:
    """
    A specification of a region of the screen.

    The region is defined by four coordinates:
    - width_x and width_y define a line segment in the x and y directions.
    - height_x and height_y define a line segment in the x and y directions.
    """

    width_x: float
    width_y: float
    height_x: float
    height_y: float

    @classmethod
    def top_left(cls):
        """
        Returns a RegionSpec representing the top left corner of the screen.
        """
        return cls(width_x=0, width_y=0.5, height_x=0.5, height_y=1)

    @classmethod
    def top_right(cls):
        """
        Returns a RegionSpec representing the top right corner of the screen.
        """
        return cls(width_x=0.5, width_y=0.5, height_x=1, height_y=1)

    @classmethod
    def bottom_left(cls):
        """
        Returns a RegionSpec representing the bottom left corner of the screen.
        """
        return cls(width_x=0, width_y=0, height_x=0.5, height_y=0.5)

    @classmethod
    def bottom_right(cls):
        """
        Returns a RegionSpec representing the bottom right corner of the screen.
        """
        return cls(width_x=0.5, width_y=0, height_x=1, height_y=0.5)

    @classmethod
    def center(cls):
        """
        Returns a RegionSpec representing the center of the screen.
        """
        return cls(width_x=0.25, width_y=0.75, height_x=0.25, height_y=0.75)

    @classmethod
    def full(cls):
        """
        Returns a RegionSpec representing the entire screen.
        """
        return cls(width_x=0, width_y=1, height_x=0, height_y=1)

    @property
    def isFull(self):
        """
        Returns whether this RegionSpec represents the entire screen.
        """
        return (
            self.width_x == 0
            and self.width_y == 1
            and self.height_x == 0
            and self.height_y == 1
        )


@dataclass
class RegionMarker:
    """
    A marker for a region of the screen.

    The marker can be associated with a specific window or monitor.
    """

    region: RegionSpec = field(default_factory=RegionSpec.full)
    monitor_num: Optional[int] = None
    window: Optional[gw.Window] = None
    allscreens: bool = False

    @classmethod
    def all_screens(cls):
        """
        Returns a RegionMarker that captures all screens.
        """
        return cls(allscreens=True)

    @classmethod
    def from_window(
        cls, window: gw.Window, region: Optional[RegionSpec] = None
    ):
        """
        Returns a RegionMarker associated with the given window.

        The region is optional and defaults to the entire screen.
        """
        return cls(window=window, region=region if region else RegionSpec.full())

    @classmethod
    def from_monitor(
        cls, monitor_num: int, region: Optional[RegionSpec] = None
    ):
        """
        Returns a RegionMarker associated with the given monitor.

        The region is optional and defaults to the entire screen.
        """
        return cls(
            monitor_num=monitor_num,
            region=region if region else RegionSpec.full(),
        )

    def __post_init__(self):
        self.__screenshotted = False
        self.__monitor_num_mirror = self.monitor_num
        self.__window_coords_mirror = None


    @property
    def screenshot(self):
        """
        Returns a screenshot of the specified region of the screen.

        If a window is specified, the screenshot is taken of the entire window.
        If a monitor number is specified, the screenshot is taken of the entire monitor.
        If neither a window nor a monitor number is specified, the screenshot is taken of the entire screen.

        If a RegionSpec is provided, the screenshot is taken of the specified region within the window or monitor.

        Returns:
            PIL.Image.Image: The screenshot image.
        """
        if self.window:
            wnd_pos = get_window_pos(self.window)
            self.__window_coords_mirror = copy.deepcopy(wnd_pos)
            bbox = (
                wnd_pos[0],
                wnd_pos[1],
                wnd_pos[0] + wnd_pos[2],
                wnd_pos[1] + wnd_pos[3],
            )
        elif self.monitor_num is not None:
            bbox = get_monitor_bounds(self.monitor_num)

        # Adjust the region based on the RegionSpec if not capturing all screens
        if bbox and not self.region.isFull:
            x1, y1, x2, y2 = bbox
            new_x1 = x1 + self.region.width_x * (x2 - x1)
            new_y1 = y1 + self.region.height_x * (y2 - y1)
            new_x2 = x1 + self.region.width_y * (x2 - x1)
            new_y2 = y1 + self.region.height_y * (y2 - y1)
            bbox = (new_x1, new_y1, new_x2, new_y2)

        # Take the screenshot using PIL
        image = ImageGrab.grab(bbox, all_screens=self.allscreens)
        self.__screenshotted = True
        return image

    @property
    def mutated(self):
        """
        Check if the RegionMarker has been mutated.

        Returns:
            bool: True if the RegionMarker has been mutated, False otherwise.
        """
        if not self.__screenshotted:
            return False

        if (
            self.__window_coords_mirror is not None
            and get_window_pos(self.window) != self.__window_coords_mirror
        ):
            return True

        if self.__monitor_num_mirror != self.monitor_num:
            return True

        return False
