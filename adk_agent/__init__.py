"""
ADK Agent Package - Google Agent Development Kit Implementation
Standard structure for adk run and adk web compatibility
"""

from .agent import root_agent, fetch_and_store_webpage, get_content_summary, webpage_storage

__all__ = ['root_agent', 'fetch_and_store_webpage', 'get_content_summary', 'webpage_storage']
