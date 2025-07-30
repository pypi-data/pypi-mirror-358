from abc import ABC, abstractmethod
import re


class BaseOperation(ABC):
    """Base class for all operations in the pipeline."""
    
    def __init__(self, *args, **kwargs):
        """Initialize operation with parameters."""
        self.args = args
        self.kwargs = kwargs
    
    def __call__(self, *args, **kwargs):
        """Make operation callable."""
        return self.apply(*args, **kwargs)
    
    @staticmethod
    def _get_operation_name(operation_class):
        """Get the operation name from a class.
        
        Args:
            operation_class: The operation class
            
        Returns:
            str: The operation name in snake_case
        """
        name = operation_class.__name__
        name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
        name = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', name).lower()
        
        # Remove common suffixes
        for suffix in ['_operation', '_producer', '_consumer']:
            if name.endswith(suffix):
                return name[:-len(suffix)]
        return name


class Operation(BaseOperation):
    """Base class for image processing operations (ImgPack in, ImgPack out)."""
    
    @abstractmethod
    def apply(self, img_pack):
        """Apply the operation to an ImgPack and return a new ImgPack.
        
        Args:
            img_pack: ImgPack instance to process
            
        Returns:
            ImgPack: New ImgPack instance with operation applied
        """
        pass

    @classmethod
    def register(cls, name_or_class=None):
        """Register this operation with ImgPack.
        
        Preferred usage:
        @Operation.register  # Infers name from class name (recommended)
        class MyOperation(Operation):
            ...
            
        Alternative usages:
        @Operation.register('custom_name')  # Explicit name
        MyOperation.register()  # Manual registration (for tests)
        
        Args:
            name_or_class: Either a name string or a class (when used as decorator)
        """
        # Import moved to top of file when needed
        from .image_pack import ImgPack
        
        def _register_operation(operation_class, operation_name=None):
            """Helper function to register an operation."""
            if operation_name is None:
                operation_name = BaseOperation._get_operation_name(operation_class)
            ImgPack.register_operation(operation_name, operation_class)
            return operation_class
        
        # Preferred case: @Operation.register (no arguments)
        if name_or_class is None:
            # Return a decorator function
            return lambda operation_class: _register_operation(operation_class)
        
        # Alternative case: @Operation.register('name') or called with string
        if isinstance(name_or_class, str):
            # Return a decorator function when string is provided
            return lambda operation_class: _register_operation(operation_class, name_or_class)
        
        # Direct registration case (primarily for backward compatibility)
        else:
            # Direct registration of the class
            return _register_operation(name_or_class)


class Consumer(BaseOperation):
    """Base class for operations that consume an ImgPack without returning one."""

    @abstractmethod
    def apply(self, img_pack):
        """Apply the operation to an ImgPack.

        Args:
            img_pack: ImgPack instance to process
        """
        pass