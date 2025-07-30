import re
from typing import Dict, Set


class ContextData:
    """Base class for all context data classes.
    
    This class acts as a bridge for data transfer between producers (operations)
    and consumers. It maintains a registry of which operations produce which
    context data types.
    """
    
    # Registry for operations that produce each context type
    _producer_operations: Dict[str, Set[str]] = {}
    
    @classmethod
    def _get_context_name(cls):
        """Get the context name from the class name.
        
        Returns:
            str: The context name in snake_case
        """
        name = cls.__name__
        name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
        name = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', name).lower()
        
        if name.endswith('_context_data'):
            return name[:-len('_context_data')]
        elif name.endswith('_context'):
            return name[:-len('_context')]
        else:
            return name
    
    @classmethod
    def register_as_producer(cls, operation_class=None):
        """Decorator to register an operation as a producer of this context type.
        
        Usage:
        @ResolutionDecisionContextData.register_as_producer
        class DecideResolutionOperation(BaseOperation):
            ...
        """
        def decorator(op_class):
            # Local import to avoid circular dependency
            from .operation import BaseOperation
            
            operation_name = BaseOperation._get_operation_name(op_class)
            context_name = cls._get_context_name()
            cls.register_producer_operation(context_name, operation_name)
            return op_class
        
        if operation_class is not None:
            return decorator(operation_class)
        
        return decorator
    
    @classmethod
    def register_producer_operation(cls, context_name: str, operation_name: str) -> None:
        """Register an operation as a producer of a specific context type.
        
        Args:
            context_name: Name of the context type
            operation_name: Name of the operation that produces this context
        """
        if context_name not in cls._producer_operations:
            cls._producer_operations[context_name] = set()
        cls._producer_operations[context_name].add(operation_name)
    
    @classmethod
    def get_producer_operations(cls, context_name: str) -> Set[str]:
        """Get operations that produce a specific context type.
        
        Args:
            context_name: Name of the context type
            
        Returns:
            Set of operation names that produce this context
        """
        return cls._producer_operations.get(context_name, set())
    
    @classmethod
    def get_all_producer_operations(cls) -> Dict[str, Set[str]]:
        """Get all producer operations for all context types.
        
        Returns:
            Dictionary mapping context names to sets of producer operation names
        """
        return cls._producer_operations.copy()     
    def __repr__(self) -> str:
        """String representation of context data."""
        return f"{self.__class__.__name__}({self._data})"
    
    def __eq__(self, other) -> bool:
        """Check equality with another context data instance."""
        if not isinstance(other, ContextData):
            return False
        return self._data == other._data
