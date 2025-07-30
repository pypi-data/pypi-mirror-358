from PIL import Image, ImageFilter
from ..core.operation import Operation
from ..contexts.blur import BlurContextData

@BlurContextData.register_as_producer
@Operation.register
class BlurOperation(Operation):
    """
    Apply blur effect to the image.
    """
    
    def __init__(self, radius=2):
        """Initialize blur operation.
        
        Args:
            radius: Blur radius (default: 2)
        """
        super().__init__(radius=radius)
        self.radius = radius
    
    def apply(self, img_pack):
        """
        Apply blur effect to the image.
        
        Args:
            img_pack: ImgPack instance
            
        Returns:
            ImgPack: New instance with blurred image
        """
        blurred_img = img_pack.pil_img.filter(ImageFilter.GaussianBlur(radius=self.radius))
        
        # Create structured blur context data
        blur_context = BlurContextData(
            blur_applied=True,
            blur_radius=self.radius
        )
        
        # Create new img_pack with structured context
        new_pack = img_pack.copy(new_img=blurred_img)
        new_pack.add_context(blur_context)
        
        return new_pack