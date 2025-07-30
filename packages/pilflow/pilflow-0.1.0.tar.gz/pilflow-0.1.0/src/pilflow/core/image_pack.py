
from typing import Dict, Any, Optional, Union
from PIL import Image
from .context import ContextData

class ImgPack:
    """Base class for image processing pipeline with structured context support."""
    
    # Registry for operations
    _operations = {}
    
    def __init__(self, pil_img, context_data=None, image_format: Optional[str] = None):
        self.pil_img = pil_img
        self._context_data = context_data if context_data is not None else {}
        self._structured_contexts: Dict[str, ContextData] = {}
        self.image_format = image_format # Store the image format (e.g., 'jpeg', 'png')

    @property
    def context(self):
        """Return the context data dictionary."""
        return self._context_data
    
    @property
    def img(self):
        """Return the PIL image object."""
        return self.pil_img

    @property
    def base64(self) -> str:
        """Return the base64 encoded string of the PIL image.

        The image is saved using its original format if available, otherwise PNG.
        """
        import base64
        from io import BytesIO
        
        buffered = BytesIO()
        format_to_use = self.image_format if self.image_format else "PNG"
        self.pil_img.save(buffered, format=format_to_use)
        payload = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return f"data:image/{format_to_use.lower()};base64,{payload}"

    @staticmethod
    def from_base64(base64_string: str, **kwargs) -> 'ImgPack':
        """Create an ImgPack instance from a base64 encoded string.

        Args:
            base64_string: The base64 encoded string of the image.
            **kwargs: Additional context data to initialize the ImgPack.

        Returns:
            ImgPack: A new ImgPack instance.

        Raises:
            ValueError: If the base64 string is invalid or cannot be decoded.
            PIL.UnidentifiedImageError: If the decoded data is not a valid image.
        """
        import base64
        import binascii
        import re
        from io import BytesIO
        import PIL
        
        try:
            # Check for data URI prefix (e.g., data:image/jpeg;base64,...)
            match = re.match(r"data:image/([a-zA-Z0-9]+);base64,", base64_string)
            image_format = None
            if match:
                image_format = match.group(1).upper()
                # PIL uses 'JPEG' for 'jpeg'
                if image_format == 'JPEG':
                    image_format = 'JPEG'
                # Remove the prefix before decoding
                base64_data = base64_string[match.end():]
            else:
                base64_data = base64_string

            image_data = base64.b64decode(base64_data)
            pil_img = Image.open(BytesIO(image_data))
            return ImgPack(pil_img, context_data=kwargs, image_format=image_format)
        except (binascii.Error, ValueError) as e:
            raise ValueError(f"Invalid base64 string: {str(e)}")
        except PIL.UnidentifiedImageError as e:
            raise PIL.UnidentifiedImageError(f"Decoded data is not a valid image: {str(e)}")

    @staticmethod
    def from_file(file_path: str, **kwargs) -> 'ImgPack':
        """Create an ImgPack instance from an image file.

        Args:
            file_path: Path to the image file.
            **kwargs: Additional context data to initialize the ImgPack.

        Returns:
            ImgPack: A new ImgPack instance.

        Raises:
            FileNotFoundError: If the file does not exist.
            PIL.UnidentifiedImageError: If the file is not a valid image.
        """
        import os
        import PIL
        
        try:
            pil_img = Image.open(file_path)
            # Infer format from file extension
            file_extension = os.path.splitext(file_path)[1].lstrip('.').upper()
            # PIL uses 'JPEG' for '.jpg' and '.jpeg'
            if file_extension == 'JPG':
                file_extension = 'JPEG'
            return ImgPack(pil_img, context_data=kwargs, image_format=file_extension)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Image file not found: {file_path}")
        except PIL.UnidentifiedImageError as e:
            raise PIL.UnidentifiedImageError(f"File is not a valid image: {file_path}")
    
    def copy(self, new_img=None, **context_updates) -> 'ImgPack':
        """Create a new ImgPack instance with optional updates.
         
         Args:
             new_img: Optional new PIL image to use
             **context_updates: Additional context data to update
             
         Returns:
             ImgPack: A new ImgPack instance with copied image and context data.
         """
        img = new_img if new_img is not None else self.pil_img
        new_context = self._context_data.copy()
        new_context.update(context_updates)
        new_pack = ImgPack(img, new_context)
        # Deep copy structured contexts
        new_pack._structured_contexts = self._structured_contexts.copy()
        return new_pack
    
    def add_context(self, context_data: ContextData, name: Optional[str] = None) -> None:
        """Add structured context data to the image pack.
        
        Args:
            context_data: ContextData instance to add
            name: Optional name for the context (inferred from class if not provided)
        """
        if name is None:
            # Infer name from context class using _get_context_name method
            context_class = type(context_data)
            name = context_class._get_context_name()
        
        self._structured_contexts[name] = context_data
    
    def get_context(self, name: str) -> Optional[ContextData]:
        """Get structured context data by name.
        
        Args:
            name: Name of the context data
            
        Returns:
            ContextData instance or None if not found
        """
        return self._structured_contexts.get(name)
    
    def has_context(self, name: str) -> bool:
        """Check if structured context data exists.
        
        Args:
            name: Name of the context data
            
        Returns:
            True if context exists, False otherwise
        """
        return name in self._structured_contexts
    
    def remove_context(self, name: str) -> bool:
        """Remove structured context data.
        
        Args:
            name: Name of the context data to remove
            
        Returns:
            True if context was removed, False if it didn't exist
        """
        if name in self._structured_contexts:
            del self._structured_contexts[name]
            return True
        return False
    
    def get_all_contexts(self) -> Dict[str, ContextData]:
        """Get all structured context data.
        
        Returns:
            Dictionary of all structured contexts
        """
        return self._structured_contexts.copy()
    
    def to_json(self) -> str:
        """Convert ImgPack to JSON string.
        
        Returns:
            JSON string representation including image and contexts
        """
        import json
        
        # Serialize structured contexts
        structured_contexts = {}
        for name, context in self._structured_contexts.items():
            structured_contexts[name] = context.to_dict()
        
        data = {
            'image_base64': self.base64,
            'context_data': self._context_data,
            'structured_contexts': structured_contexts
        }
        
        return json.dumps(data, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str, pil_img: Optional[Image.Image] = None) -> 'ImgPack':
        """Create ImgPack from JSON string.
        
        Args:
            json_str: JSON string containing ImgPack data
            pil_img: Optional PIL image to use instead of the one in JSON
            
        Returns:
            ImgPack instance
        """
        import json
        
        data = json.loads(json_str)
        
        # Use provided image or decode from base64
        if pil_img is not None:
            img = pil_img
        else:
            img = cls.from_base64(data['image_base64']).pil_img
        
        # Create ImgPack with legacy context data
        img_pack = cls(img, data.get('context_data', {}))
        
        # Restore structured contexts
        for name, context_data in data.get('structured_contexts', {}).items():
            context_class = ContextData.get_context_class(name)
            if context_class:
                context = context_class.from_dict(context_data)
                img_pack._structured_contexts[name] = context
        
        return img_pack
    
    def get_missing_contexts(self, required_contexts: list) -> list:
        """Get list of missing required contexts for logging purposes.
        
        Args:
            required_contexts: List of required context names
            
        Returns:
            List of missing context names
        """
        missing = []
        for context_name in required_contexts:
            if not self.has_context(context_name):
                missing.append(context_name)
        return missing
    
    def log_missing_contexts(self, required_contexts: list, operation_name: str = "operation") -> None:
        """Log missing contexts and suggest generator operations.
        
        Args:
            required_contexts: List of required context names
            operation_name: Name of the operation requiring contexts
        """
        missing = self.get_missing_contexts(required_contexts)
        if missing:
            print(f"Warning: {operation_name} requires missing contexts: {missing}")
            
            # Suggest producer operations based on registered producers
            suggestions = []
            for context_name in missing:
                producer_operations = ContextData.get_producer_operations(context_name)
                if producer_operations:
                    for producer_op in producer_operations:
                        suggestions.append(f"  - Run '{producer_op}' operation to generate '{context_name}' context")
                else:
                    # Fallback to heuristic approach if no producers registered
                    context_class = ContextData.get_context_class(context_name)
                    if context_class:
                        for op_name, op_class in self._operations.items():
                            if (context_name in op_name.lower() or 
                                (hasattr(op_class, '__doc__') and op_class.__doc__ and 
                                 context_name in op_class.__doc__.lower())):
                                suggestions.append(f"  - Run '{op_name}' operation to generate '{context_name}' context (heuristic)")
            
            if suggestions:
                print("Suggested operations to generate missing contexts:")
                for suggestion in suggestions:
                    print(suggestion)
    
    @classmethod
    def register_operation(cls, name, operation_class):
        """Register an operation class."""
        cls._operations[name] = operation_class
    
    def __getattr__(self, name):
        """Dynamically create operation methods."""
        if name in self._operations:
            operation_class = self._operations[name]
            def operation_method(*args, **kwargs):
                operation = operation_class(*args, **kwargs)
                return operation(self)
            return operation_method
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
