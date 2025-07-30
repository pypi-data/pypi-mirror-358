from jinnang.media.resolution import ResolutionPreset
from ..core.operation import Operation
from ..contexts.resolution_decision import ResolutionDecisionContextData
from jinnang.media.resolution import ResolutionPreset


@ResolutionDecisionContextData.register_as_producer
@Operation.register
class DecideResolutionOperation(Operation):
    """Operation to decide target resolution using ResolutionPreset.
    
    This operation stores the ResolutionPreset in context without
    actually resizing the image. The resize operation will read
    this context to perform the actual resizing.
    """
    
    def __init__(self, resolution_preset=None):
        """Initialize decide resolution operation.
        
        Args:
            resolution_preset: ResolutionPreset enum value (defaults to ORIGINAL)
        """
        if resolution_preset is None:
            resolution_preset = ResolutionPreset.ORIGINAL
        super().__init__(resolution_preset=resolution_preset)
        self.resolution_preset = resolution_preset
    
    def apply(self, img_pack):
        """Apply resolution decision to the image pack.
        
        Args:
            img_pack: ImgPack instance
            
        Returns:
            ImgPack: New instance with resolution decision in context
        """
        # Create resolution decision context with the ResolutionPreset
        resolution_decision_context = ResolutionDecisionContextData(
            resolution_preset=self.resolution_preset
        )
        
        # Create new img_pack with resolution decision context
        new_pack = img_pack.copy()
        new_pack.add_context(resolution_decision_context)
        
        return new_pack