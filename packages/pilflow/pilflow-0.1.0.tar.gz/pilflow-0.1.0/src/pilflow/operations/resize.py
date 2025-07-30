from PIL import Image
from ..core.operation import Operation
from ..contexts.resize import ResizeContextData
from ..contexts.resolution_decision import ResolutionDecisionContextData

@ResizeContextData.register_as_producer
@Operation.register
class ResizeOperation(Operation):
    """
    Resize the image based on context or provided dimensions.
    """
    
    def __init__(self, width=None, height=None, resolution_preset=None):
        """Initialize resize operation with target dimensions or resolution preset.
        
        Args:
            width: Target width (optional)
            height: Target height (optional)
            resolution_preset: ResolutionPreset enum value (optional)
        """
        super().__init__(width=width, height=height, resolution_preset=resolution_preset)
        self.width = width
        self.height = height
        self.resolution_preset = resolution_preset
    
    def apply(self, img_pack):
        """
        Resize the image based on ResolutionDecision context data.
        
        Args:
            img_pack: ImgPack instance
            
        Returns:
            ImgPack: New instance with resized image
            
        Raises:
            ValueError: If no ResolutionDecision context is found
        """
        current_img = img_pack.pil_img
        width = self.width
        height = self.height
        
        # If resolution_preset is provided directly, use it
        if self.resolution_preset is not None:
            target_width, target_height = self.resolution_preset.value
            
            # Handle ORIGINAL preset (None, None)
            if target_width is None or target_height is None:
                width = current_img.width
                height = current_img.height
            else:
                width = target_width
                height = target_height
        
        # If no dimensions provided, require ResolutionDecision context
        if width is None and height is None:
            resolution_decision_context = img_pack.get_context('resolution_decision')
            if not resolution_decision_context:
                raise ValueError(
                    "ResizeOperation requires explicit dimensions or a ResolutionDecision context. "
                    "Use ResolutionDecisionContextData to provide resize dimensions, "
                    "which can be produced by DecideResolutionOperation."
                )
            
            # Extract width and height from the resolution preset
            target_width, target_height = resolution_decision_context.resolution_preset.value
            
            # Handle ORIGINAL preset (None, None)
            if target_width is None or target_height is None:
                width = current_img.width
                height = current_img.height
            else:
                width = target_width
                height = target_height
        
        # Calculate missing dimension while preserving aspect ratio
        if width is None and height is not None:
            aspect_ratio = current_img.width / current_img.height
            width = int(height * aspect_ratio)
        elif height is None and width is not None:
            aspect_ratio = current_img.width / current_img.height
            height = int(width / aspect_ratio)
        
        # Resize the image
        resized_img = current_img.resize((width, height), Image.Resampling.LANCZOS)
        
        # Create structured resize context data
        resize_context = ResizeContextData(
            current_width=width,
            current_height=height,
            resized=True,
            resize_width=width,
            resize_height=height,
            target_width=self.width,
            target_height=self.height
        )
        
        # Create new img_pack with structured context
        new_pack = img_pack.copy(new_img=resized_img)
        new_pack.add_context(resize_context)
        
        return new_pack