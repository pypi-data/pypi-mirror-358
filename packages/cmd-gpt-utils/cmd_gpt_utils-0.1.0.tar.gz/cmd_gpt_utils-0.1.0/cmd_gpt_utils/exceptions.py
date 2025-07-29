class CmdGptError(Exception):
    """Base exception class for cmd_gpt."""
    pass

class ConfigError(CmdGptError):
    """Raised for configuration-related errors."""
    pass

class ModelError(CmdGptError):
    """Raised for model selection errors."""
    pass

class APIError(CmdGptError):
    """Raised for API call errors."""
    pass
