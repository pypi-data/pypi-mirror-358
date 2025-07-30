from ..core.context import ContextData


class ResolutionDecisionContextData(ContextData):
    """Context data for resolution decision operations.
    
    This context stores the target resolution preset
    for use by resize operations.
    """
    
    def __init__(self, resolution_preset):
        """Initialize resolution decision context data.
        
        Args:
            resolution_preset: ResolutionPreset enum value
        """
        self.resolution_preset = resolution_preset