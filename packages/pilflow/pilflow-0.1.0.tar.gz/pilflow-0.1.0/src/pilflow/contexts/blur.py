from typing import Union
from ..core.context import ContextData


class BlurContextData(ContextData):
    """Context data for image blur information.
    
    This class stores information about blur operations applied to images,
    including blur radius and application status.
    """
    
    def __init__(self, blur_applied: bool, blur_radius: Union[int, float], **kwargs):
        """Initialize blur context data.
        
        Args:
            blur_applied: Whether blur has been applied to the image
            blur_radius: Radius of the blur effect
            **kwargs: Additional context data
        """
        self.blur_applied = blur_applied
        self.blur_radius = blur_radius

    def is_light_blur(self) -> bool:
        """Check if this is a light blur (radius <= 2)."""
        return self.blur_applied and self.blur_radius <= 2

    def is_medium_blur(self) -> bool:
        """Check if this is a medium blur (2 < radius <= 5)."""
        return self.blur_applied and 2 < self.blur_radius <= 5

    def is_heavy_blur(self) -> bool:
        """Check if this is a heavy blur (radius > 5)."""
        return self.blur_applied and self.blur_radius > 5

    def get_blur_intensity(self) -> str:
        """Get blur intensity as a string.
        
        Returns:
            String describing blur intensity: 'none', 'light', 'medium', or 'heavy'
        """
        if not self.blur_applied:
            return 'none'
        elif self.is_light_blur():
            return 'light'
        elif self.is_medium_blur():
            return 'medium'
        else:
            return 'heavy'