"""
Global configuration for journalist package.
"""

class JournalistConfig:
    """Centralized configuration for Journalist class."""
    
    # Default values
    DEFAULT_BASE_WORKSPACE_PATH = ".journalist_workspace"
    
    def __init__(self):
        """Initialize configuration with defaults."""
        self.base_workspace_path = self.DEFAULT_BASE_WORKSPACE_PATH
    
    @classmethod
    def get_base_workspace_path(cls) -> str:
        """Get base workspace path."""
        return cls.DEFAULT_BASE_WORKSPACE_PATH
