# Operations module for pilflow pipeline components
# Import all operations to trigger registration

from . import decide_resolution
from . import resize
from . import blur
from . import sharpen

# This ensures all operations are registered when the package is imported