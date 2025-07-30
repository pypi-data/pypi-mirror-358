from ..core.operation import Operation
from ..contexts.sharpen import SharpenContextData
from PIL import ImageFilter

@SharpenContextData.register_as_producer
@Operation.register
class SharpenOperation(Operation):
    """
    Apply sharpen effect to the image.
    """
    
    def __init__(self, radius=2, percent=150, threshold=3):
        """Initialize sharpen operation.
        
        Args:
            radius: Blur radius (default: 2)
            percent: Sharpening amount in percent (default: 150)
            threshold: Minimum brightness difference to apply sharpening (default: 3)
        """
        super().__init__(radius=radius, percent=percent, threshold=threshold)
        self.radius = radius
        self.percent = percent
        self.threshold = threshold
    
    def apply(self, img_pack):
        """
        Apply sharpen effect to the image.
        
        Args:
            img_pack: ImgPack instance
            
        Returns:
            ImgPack: New instance with sharpened image
        """
        sharpened_img = img_pack.pil_img.filter(ImageFilter.UnsharpMask(radius=self.radius, percent=self.percent, threshold=self.threshold))
        
        sharpen_context = SharpenContextData(
            sharpen_applied=True,
            sharpen_radius=self.radius,
            sharpen_percent=self.percent,
            sharpen_threshold=self.threshold
        )
        
        new_pack = img_pack.copy(new_img=sharpened_img)
        new_pack.add_context(sharpen_context)
        
        return new_pack