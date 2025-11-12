#!/usr/bin/env python3
"""
Setup verification script for Google ADK Web Crawling Chatbot.
Run this to verify your installation and configuration.
"""

import sys
import os

def check_imports():
    """Check if all required packages are installed."""
    print("🔍 Checking required packages...")
    
    required_packages = [
        ("streamlit", "Streamlit UI framework"),
        ("requests", "HTTP library for web scraping"),
        ("bs4", "BeautifulSoup for HTML parsing"),
        ("google.adk", "Google Agent Development Kit"),
        ("google.genai", "Google Generative AI"),
        ("dotenv", "Environment variable management"),
    ]
    
    optional_packages = [
        ("lxml", "Fast XML/HTML parser"),
        ("html2text", "HTML to text conversion"),
    ]
    
    all_good = True
    
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package:30} - {description}")
        except ImportError:
            print(f"  ❌ {package:30} - {description} (MISSING)")
            all_good = False
    
    print("\n🔧 Optional packages:")
    for package, description in optional_packages:
        try:
            __import__(package)
            print(f"  ✅ {package:30} - {description}")
        except ImportError:
            print(f"  ⚠️  {package:30} - {description} (optional)")
    
    return all_good


def check_env_file():
    """Check if .env file exists and has required variables."""
    print("\n📄 Checking environment configuration...")
    
    if not os.path.exists(".env"):
        print("  ⚠️  .env file not found")
        print("  💡 Copy .env.example to .env and configure your Google API key")
        return False
    
    print("  ✅ .env file exists")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check for Google API key (REQUIRED for ADK)
    google_key = os.getenv("GOOGLE_API_KEY")
    
    print("\n  API Key Status:")
    if google_key and google_key != "your_google_api_key_here":
        print("    ✅ GOOGLE_API_KEY configured")
        print(f"    ℹ️  Key: ...{google_key[-8:]}")
        return True
    else:
        print("    ❌ GOOGLE_API_KEY not configured (REQUIRED)")
        print("    💡 Get your API key from: https://aistudio.google.com/app/apikey")
        return False


def check_adk_agent():
    """Check if ADK agent can be created."""
    print("\n� Checking Google ADK setup...")
    
    try:
        from google.adk.agents.llm_agent import Agent
        from google.genai import types
        
        print("  ✅ ADK imports successful")
        
        # Check if we can create a basic agent config
        try:
            config = types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=100
            )
            print("  ✅ Can create GenerateContentConfig")
        except Exception as e:
            print(f"  ❌ Error creating config: {e}")
            return False
        
        # Check API key
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key and google_key != "your_google_api_key_here":
            print("  ✅ Google API key available for agent")
            return True
        else:
            print("  ❌ Google API key needed to create agent")
            return False
            
    except ImportError as e:
        print(f"  ❌ ADK import failed: {e}")
        print("  💡 Install with: pip install google-adk google-genai")
        return False
    except Exception as e:
        print(f"  ❌ Error checking ADK: {e}")
        return False


def test_web_scraping():
    """Test web scraping functionality."""
    print("\n🕷️  Testing web scraping...")
    
    try:
        from web_utils import fetch_webpage_content
        
        test_url = "https://example.com"
        print(f"  Testing with: {test_url}")
        
        success, content = fetch_webpage_content(test_url, max_words=100)
        
        if success:
            print("  ✅ Web scraping works!")
            print(f"  ℹ️  Fetched {len(content.split())} words")
        else:
            print(f"  ❌ Web scraping failed: {content}")
            
    except Exception as e:
        print(f"  ❌ Error testing web scraping: {e}")


def main():
    """Run all checks."""
    print("=" * 70)
    print("🕷️  Google ADK Web Crawling Chatbot - Setup Verification")
    print("=" * 70)
    
    # Check Python version
    print(f"\n🐍 Python version: {sys.version.split()[0]}")
    if sys.version_info < (3, 9):
        print("  ⚠️  Python 3.9+ recommended")
    else:
        print("  ✅ Python version OK")
    
    # Run checks
    imports_ok = check_imports()
    env_ok = check_env_file()
    adk_ok = check_adk_agent()
    
    if imports_ok:
        test_web_scraping()
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 Summary")
    print("=" * 70)
    
    if imports_ok and env_ok and adk_ok:
        print("\n✅ Setup looks good! You can run the app with:")
        print("\n   streamlit run app.py\n")
        print("📚 Learn more about Google ADK:")
        print("   https://google.github.io/adk-docs/\n")
    else:
        print("\n⚠️  Some issues found. Please resolve them before running the app.")
        
        if not imports_ok:
            print("\n   Install dependencies:")
            print("   pip install -r requirements.txt")
        
        if not env_ok or not adk_ok:
            print("\n   Configure Google API key:")
            print("   1. Get key from: https://aistudio.google.com/app/apikey")
            print("   2. Copy .env.example to .env")
            print("   3. Add: GOOGLE_API_KEY=your_key_here")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
