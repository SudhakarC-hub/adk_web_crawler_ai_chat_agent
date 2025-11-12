"""
Configuration management for Web Crawling Chatbot using Google ADK.
Handles environment variables and model configurations.
"""

import os
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration for Google ADK agent."""
    
    # Model configurations
    # Note: ADK primarily works with Gemini models, but can be extended
    MODEL_BACKENDS = ["gemini", "ollama"]
    
    MODEL_OPTIONS = {
        "gemini": {
            "models": [
                "gemini-2.0-flash",
                "gemini-2.0-flash-exp", 
                "gemini-1.5-flash", 
                "gemini-1.5-pro",
                "gemini-2.5-flash"  # Latest model
            ],
            "default": "gemini-2.0-flash",
            "requires_api_key": True,
            "api_key_env": "GOOGLE_API_KEY"
        },
        "ollama": {
            "models": ["mistral:latest", "llama2:latest", "codellama:latest", "gemma:latest", "phi:latest"],
            "default": "mistral:latest",
            "requires_api_key": False,
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        }
    }
    
    # Default settings
    DEFAULT_MODEL_BACKEND = os.getenv("DEFAULT_MODEL_BACKEND", "ollama")
    DEFAULT_MODEL_NAME = os.getenv("DEFAULT_MODEL_NAME", "mistral")
    
    # Web scraping settings
    MAX_WORDS = int(os.getenv("MAX_WORDS", "25000"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # ADK Agent settings
    DEFAULT_TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
    DEFAULT_MAX_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "2048"))
    CONTEXT_WINDOW = int(os.getenv("CONTEXT_WINDOW", "32768"))
    
    # ADK Session settings
    APP_NAME = "WebCrawlerADKChatAgent"
    AGENT_NAME = "web_chat_agent"
    AGENT_DESCRIPTION = "AI assistant that answers questions based on crawled webpage content"
    
    @classmethod
    def get_model_options(cls, backend: str) -> List[str]:
        """Get available models for a backend."""
        return cls.MODEL_OPTIONS.get(backend, {}).get("models", [])
    
    @classmethod
    def get_default_model(cls, backend: str) -> str:
        """Get default model for a backend."""
        return cls.MODEL_OPTIONS.get(backend, {}).get("default", "")
    
    @classmethod
    def requires_api_key(cls, backend: str) -> bool:
        """Check if backend requires API key."""
        return cls.MODEL_OPTIONS.get(backend, {}).get("requires_api_key", False)
    
    @classmethod
    def get_api_key(cls, backend: str) -> str:
        """Get API key for a backend."""
        if not cls.requires_api_key(backend):
            return None
        
        env_var = cls.MODEL_OPTIONS.get(backend, {}).get("api_key_env")
        return os.getenv(env_var) if env_var else None
    
    @classmethod
    def validate_backend_config(cls, backend: str) -> Dict[str, any]:
        """
        Validate backend configuration.
        
        Returns:
            Dict with 'valid' bool and 'message' str
        """
        if backend not in cls.MODEL_BACKENDS:
            return {
                "valid": False,
                "message": f"Invalid backend: {backend}"
            }
        
        if cls.requires_api_key(backend):
            api_key = cls.get_api_key(backend)
            if not api_key:
                env_var = cls.MODEL_OPTIONS[backend]["api_key_env"]
                return {
                    "valid": False,
                    "message": f"API key not found. Please set {env_var} in .env file"
                }
        
        return {
            "valid": True,
            "message": "Configuration valid"
        }


# System prompt for the ADK agent
SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions based ONLY on the provided webpage content.

Guidelines:
1. Only use information from the webpage content provided in the context.
2. If the answer is not found in the provided content, respond with: "Not found in page."
3. Be concise and specific in your answers.
4. Quote relevant parts of the content when answering.
5. Do not make up information or use external knowledge.
6. If the user asks about something not in the content, clearly state it's not available.

The webpage content is available in the {webpage_content} variable."""


# Future enhancement: Multiple system prompts for different use cases
PROMPT_TEMPLATES = {
    "default": SYSTEM_PROMPT,
    "summarization": """You are an expert at summarizing webpage content. 
Provide concise, well-structured summaries of the provided webpage content.""",
    "qa": """You are a precise question-answering assistant.
Answer questions based strictly on the provided webpage content.
If information is not available, say "Not found in page."  """,
    "extraction": """You are a data extraction specialist.
Extract specific information from the provided webpage content in a structured format."""
}


if __name__ == "__main__":
    # Test configuration
    print("=== Configuration Test ===")
    print(f"Default Backend: {Config.DEFAULT_MODEL_BACKEND}")
    print(f"Default Model: {Config.DEFAULT_MODEL_NAME}")
    print(f"Max Words: {Config.MAX_WORDS}")
    print(f"Request Timeout: {Config.REQUEST_TIMEOUT}")
    
    print("\n=== Model Backends ===")
    for backend in Config.MODEL_BACKENDS:
        print(f"\n{backend.upper()}:")
        print(f"  Models: {Config.get_model_options(backend)}")
        print(f"  Default: {Config.get_default_model(backend)}")
        print(f"  Requires API Key: {Config.requires_api_key(backend)}")
        
        validation = Config.validate_backend_config(backend)
        status = "✅" if validation["valid"] else "❌"
        print(f"  Status: {status} {validation['message']}")
