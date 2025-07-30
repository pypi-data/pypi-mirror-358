from typing import Union
from ..core.context import ContextData


class SharpenContextData(ContextData):
    """Context data for image sharpen information.
    
    This class stores information about sharpen operations applied to images,
    including sharpen factor and application status.
    """
    
    def __init__(self, sharpen_applied: bool, sharpen_radius: Union[int, float], sharpen_percent: Union[int, float], sharpen_threshold: Union[int, float]):
        """Initialize sharpen context data.
        
        Args:
            sharpen_applied: Whether sharpen has been applied to the image
            sharpen_radius: Radius of the sharpen effect
            sharpen_percent: Sharpening amount in percent
            sharpen_threshold: Minimum brightness difference to apply sharpening
        """
        self.sharpen_applied = sharpen_applied
        self.sharpen_radius = sharpen_radius
        self.sharpen_percent = sharpen_percent
        self.sharpen_threshold = sharpen_threshold