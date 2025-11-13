"""
ADK Web Crawling Agent - Model-Agnostic Implementation
Compatible with: adk run, adk web, adk local runner
Supports: Ollama, OpenAI GPT, Anthropic Claude, Google Gemini

This agent uses Google ADK framework with flexible model support via LiteLLM.

Environment Setup:
    # For Ollama (self-hosted, no API key)
    export MODEL_PROVIDER=ollama
    export MODEL_NAME=mistral
    export OLLAMA_API_BASE=http://localhost:11434
    
    # For OpenAI GPT
    export MODEL_PROVIDER=openai
    export MODEL_NAME=gpt-4
    export OPENAI_API_KEY=your_key_here
    
    # For Anthropic Claude
    export MODEL_PROVIDER=anthropic
    export MODEL_NAME=claude-3-sonnet-20240229
    export ANTHROPIC_API_KEY=your_key_here
    
    # For Google Gemini (via ADK native support)
    export MODEL_PROVIDER=gemini
    export MODEL_NAME=gemini-2.0-flash-exp
    export GOOGLE_API_KEY=your_key_here
    
Usage:
    # CLI: adk run adk_agent
    # Web UI: adk web
    # Python: from adk_agent import root_agent
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.adk.agents.llm_agent import Agent
from web_utils import fetch_webpage_content
from config import Config

# Storage for webpage content (in-memory, shared across sessions)
webpage_storage = {}

# Get model configuration from environment
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "ollama").lower()
MODEL_NAME = os.getenv("MODEL_NAME", "mistral")

SYSTEM_INSTRUCTION = """You are a helpful AI assistant with webpage fetching capabilities.

IMPORTANT: You have access to these tools:
1. fetch_and_store_webpage(url: str) - Fetches a webpage and stores its content
2. get_content_summary() - Returns summary of stored webpage content

Tool Usage Rules:
- When user provides a URL or asks to "fetch" or "load" a webpage, you MUST call fetch_and_store_webpage with that URL
- After fetching, inform the user about success and word count
- When answering questions, ONLY use the stored webpage content
- If no webpage is stored, tell user to provide a URL first

Examples of when to call fetch_and_store_webpage:
- "Please fetch this webpage: http://example.com"
- "Load http://example.com"
- "Get content from http://example.com"

Be accurate, concise, and only answer from the stored webpage content."""


def fetch_and_store_webpage(url: str) -> dict:
    """
    Fetch and store webpage content for question answering.
    
    This is a custom FunctionTool that will be automatically wrapped by ADK.
    
    Args:
        url: The URL of the webpage to fetch
        
    Returns:
        dict with status, message, and content information
    """
    try:
        # Fetch webpage (returns tuple: success, content)
        success, content = fetch_webpage_content(url, max_words=Config.MAX_WORDS)
        
        if not success:
            return {
                "status": "error",
                "message": content,  # content contains error message if failed
                "content": "",
                "word_count": 0
            }
        
        # Content is already cleaned by fetch_webpage_content
        words = content.split()
        word_count = len(words)
        
        # Store in memory (shared across all sessions)
        webpage_storage["url"] = url
        webpage_storage["content"] = content
        webpage_storage["word_count"] = word_count
        
        return {
            "status": "success",
            "message": f"✅ Successfully fetched and stored {word_count} words from the webpage. You can now ask questions about it.",
            "content": content[:500] + "..." if len(content) > 500 else content,  # Preview
            "word_count": word_count
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching webpage: {str(e)}",
            "content": "",
            "word_count": 0
        }


def get_content_summary(max_chars: int = 500) -> dict:
    """
    Get a summary/preview of the currently stored webpage content.
    
    Args:
        max_chars: Maximum characters to include in the summary
        
    Returns:
        dict with summary and metadata
    """
    if not webpage_storage.get("content"):
        return {
            "status": "error",
            "message": "No webpage has been fetched yet. Please use fetch_and_store_webpage first.",
            "summary": "",
            "word_count": 0
        }
    
    content = webpage_storage["content"]
    summary = content[:max_chars] + "..." if len(content) > max_chars else content
    
    return {
        "status": "success",
        "url": webpage_storage.get("url", "Unknown"),
        "summary": summary,
        "total_length": len(content),
        "word_count": webpage_storage.get("word_count", 0)
    }


def get_stored_content() -> str:
    """
    Get the full stored webpage content.
    Internal helper for agent to access content.
    
    Returns:
        The full webpage content or empty string if none stored
    """
    return webpage_storage.get("content", "")


def create_model():
    """
    Create the appropriate model based on MODEL_PROVIDER environment variable.
    Supports: ollama, openai, anthropic, gemini
    
    Returns:
        Model instance configured for the specified provider
    """
    provider = MODEL_PROVIDER
    model_name = MODEL_NAME
    
    if provider == "gemini":
        # Use ADK's native Gemini model
        from google.adk.models.gemini import Gemini
        print(f"🤖 Initializing Gemini model: {model_name}")
        return Gemini(model=model_name)
    
    else:
        # Use LiteLLM for all other providers (ollama, openai, anthropic, etc.)
        from google.adk.models.lite_llm import LiteLlm
        
        # Map providers to LiteLLM format
        if provider == "ollama":
            # Use ollama_chat provider for better compatibility
            litellm_model = f"ollama_chat/{model_name}"
            print(f"🦙 Initializing Ollama model: {model_name}")
        elif provider == "openai":
            litellm_model = model_name  # e.g., "gpt-4", "gpt-3.5-turbo"
            print(f"🔵 Initializing OpenAI model: {model_name}")
        elif provider == "anthropic":
            litellm_model = model_name  # e.g., "claude-3-sonnet-20240229"
            print(f"🟣 Initializing Anthropic Claude model: {model_name}")
        else:
            # Generic LiteLLM format
            litellm_model = f"{provider}/{model_name}"
            print(f"⚙️ Initializing {provider} model: {model_name}")
        
        return LiteLlm(model=litellm_model)


# Create the ADK agent with flexible model support
# Model is determined by MODEL_PROVIDER and MODEL_NAME environment variables
root_agent = Agent(
    model=create_model(),  # Model-agnostic initialization
    name="web_crawler",  # Agent name (not app name)
    description="AI assistant that fetches webpages and answers questions based on their content using ADK framework",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        fetch_and_store_webpage,  # ADK automatically wraps as FunctionTool
        get_content_summary,      # ADK automatically wraps as FunctionTool
    ]
)

# Export root_agent for ADK CLI compatibility
__all__ = ['root_agent', 'fetch_and_store_webpage', 'get_content_summary', 'webpage_storage']
