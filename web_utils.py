"""
Web scraping utilities for fetching and cleaning webpage content.
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional, Tuple
import re


def fetch_webpage_content(url: str, max_words: int = 25000, timeout: int = 30) -> Tuple[bool, str]:
    """
    Fetch and clean visible text content from a webpage.
    
    Args:
        url: The webpage URL to fetch
        max_words: Maximum number of words to extract (default: 25,000)
        timeout: Request timeout in seconds (default: 30)
    
    Returns:
        Tuple of (success: bool, content: str)
        If success is False, content contains the error message
    """
    try:
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            return False, "Invalid URL. Please include http:// or https://"
        
        # Fetch webpage with headers to mimic browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Remove script, style, and other non-content elements
        for element in soup(['script', 'style', 'head', 'title', 'meta', '[document]', 'noscript', 'header', 'footer', 'nav', 'aside']):
            element.decompose()
        
        # Extract visible text
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up the text
        text = clean_text(text)
        
        # Limit to max_words
        words = text.split()
        if len(words) > max_words:
            text = ' '.join(words[:max_words])
            text += f"\n\n[Content truncated at {max_words} words]"
        
        if not text or len(text.strip()) < 50:
            return False, "No meaningful content found on the webpage."
        
        # Add metadata
        page_title = soup.find('title')
        title_text = page_title.get_text().strip() if page_title else "No title"
        
        content = f"Page Title: {title_text}\n"
        content += f"URL: {url}\n"
        content += f"Word Count: {len(text.split())} words\n"
        content += f"{'-' * 80}\n\n"
        content += text
        
        return True, content
        
    except requests.exceptions.Timeout:
        return False, f"Request timeout after {timeout} seconds. The webpage took too long to respond."
    
    except requests.exceptions.ConnectionError:
        return False, "Connection error. Please check your internet connection or the URL."
    
    except requests.exceptions.HTTPError as e:
        return False, f"HTTP error occurred: {e.response.status_code} - {e.response.reason}"
    
    except requests.exceptions.RequestException as e:
        return False, f"Error fetching webpage: {str(e)}"
    
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def clean_text(text: str) -> str:
    """
    Clean and normalize extracted text.
    
    Args:
        text: Raw text extracted from HTML
    
    Returns:
        Cleaned text
    """
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove excessive newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\'\"\n]', '', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def get_content_preview(content: str, max_chars: int = 500) -> str:
    """
    Get a preview of the content for display purposes.
    
    Args:
        content: Full content text
        max_chars: Maximum characters to include in preview
    
    Returns:
        Preview string
    """
    if len(content) <= max_chars:
        return content
    
    preview = content[:max_chars]
    # Try to end at a word boundary
    last_space = preview.rfind(' ')
    if last_space > max_chars * 0.8:  # If we can cut at a nearby word
        preview = preview[:last_space]
    
    return preview + "..."


# Future enhancement hooks for RAG integration
def prepare_for_embedding(content: str) -> list[str]:
    """
    Placeholder for future RAG implementation.
    Split content into chunks suitable for embedding.
    
    Args:
        content: Full webpage content
    
    Returns:
        List of text chunks
    """
    # TODO: Implement chunk splitting for vector embedding
    # Could use LangChain's TextSplitter classes
    chunk_size = 1000
    chunks = []
    words = content.split()
    
    for i in range(0, len(words), chunk_size):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
    
    return chunks
