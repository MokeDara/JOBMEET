"""
Configuration management for JOBMEET
Handles API keys, model selection, and feature flags
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
# Try to load from parent directory (project root)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

@dataclass
class LLMConfig:
    """LLM Configuration"""
    enabled: bool = True
    provider: str = "openai"  # openai, anthropic, or gemini
    model: str = "gpt-3.5-turbo"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000


@dataclass
class AppConfig:
    """Application Configuration"""
    app_title: str = "JOBMEET - AI-Powered Resume Matcher"
    app_version: str = "2.0"
    enable_llm: bool = True
    enable_traditional_matching: bool = True  # Keep TF-IDF as fallback
    llm: LLMConfig = None
    
    def __post_init__(self):
        if self.llm is None:
            self.llm = LLMConfig()


class Config:
    """Central configuration management"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.app = AppConfig()
        self._load_from_env()
        self._initialized = True
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        # LLM Configuration
        self.app.enable_llm = os.getenv("ENABLE_LLM", "true").lower() == "true"
        self.app.enable_traditional_matching = os.getenv("ENABLE_TRADITIONAL", "true").lower() == "true"
        
        # Provider selection
        provider = os.getenv("LLM_PROVIDER", "openai").lower()
        if provider not in ["openai", "anthropic", "gemini"]:
            provider = "openai"
        self.app.llm.provider = provider
        
        # API Keys
        if provider == "openai":
            self.app.llm.api_key = os.getenv("OPENAI_API_KEY")
            self.app.llm.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        elif provider == "anthropic":
            self.app.llm.api_key = os.getenv("ANTHROPIC_API_KEY")
            self.app.llm.model = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
        elif provider == "gemini":
            self.app.llm.api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
            self.app.llm.model = os.getenv("GEMINI_MODEL", "gemini-pro")
        
        # LLM Parameters
        self.app.llm.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.app.llm.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2000"))
    
    def get_llm_config(self) -> LLMConfig:
        """Get LLM configuration"""
        return self.app.llm
    
    def has_valid_api_key(self) -> bool:
        """Check if a valid API key is configured"""
        return self.app.llm.api_key is not None and len(self.app.llm.api_key) > 0
    
    def is_llm_enabled(self) -> bool:
        """Check if LLM is enabled"""
        return self.app.enable_llm and self.has_valid_api_key()
    
    def get_info(self) -> dict:
        """Get configuration info for debugging"""
        return {
            "app_version": self.app.app_version,
            "llm_enabled": self.is_llm_enabled(),
            "llm_provider": self.app.llm.provider,
            "llm_model": self.app.llm.model,
            "traditional_matching_enabled": self.app.enable_traditional_matching,
            "api_key_configured": self.has_valid_api_key()
        }


# Global config instance
config = Config()
