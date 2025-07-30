class LLMNetError(Exception):
    """Base exception for LLMNet"""
    pass

class ConfigError(LLMNetError):
    """Configuration related errors"""
    pass

class AuthenticationError(LLMNetError):
    """Authentication related errors"""
    pass

class ServerError(LLMNetError):
    """Server related errors"""
    pass

class ModelError(LLMNetError):
    """Model assignment related errors"""
    pass