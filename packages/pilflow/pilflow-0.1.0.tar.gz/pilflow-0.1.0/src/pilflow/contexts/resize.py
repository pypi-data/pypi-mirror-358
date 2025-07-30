from typing import Optional
from ..core.context import ContextData


class ResizeContextData(ContextData):
    """Context data for image resize information.
    
    This class stores information about image resizing operations,
    target dimensions, and resize status in a structured format.
    """
    
    def __init__(self, current_width: int, current_height: int, 
                 resized: bool = False, target_width: Optional[int] = None,
                 target_height: Optional[int] = None, resize_width: Optional[int] = None,
                 resize_height: Optional[int] = None, **kwargs):
        """Initialize resize context data.
        
        Args:
            current_width: Current image width in pixels
            current_height: Current image height in pixels
            resized: Whether the image has been resized
            target_width: Target width for resizing (optional)
            target_height: Target height for resizing (optional)
            resize_width: Actual width after resize (optional)
            resize_height: Actual height after resize (optional)
            **kwargs: Additional context data
        """
        self.current_width = current_width
        self.current_height = current_height
        self.resized = resized
        self.target_width = target_width
        self.target_height = target_height
        self.resize_width = resize_width
        self.resize_height = resize_height