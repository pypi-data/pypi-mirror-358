# Import functions from your modules so users can access them directly
from .dna_tools import *

# You can define __all__ for explicit exports (optional but cleaner)
__all__ = ['gc_content', 'transcribe', 'reverse_complement']

