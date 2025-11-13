"""
Streamlit Frontend for ADK Web Crawling Agent
Uses Google Agent Development Kit (ADK) with LiteLLM + Ollama (Self-hosted Mistral)
"""

import streamlit as st
import os
from dotenv import load_dotenv
from web_utils import get_content_preview
import config as app_config

# Import ADK components
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from adk_agent import root_agent, webpage_storage, fetch_and_store_webpage

# Load environment variables
load_dotenv()
load_dotenv("adk_agent/.env")  # Also load ADK-specific config

# Page configuration
st.set_page_config(
    page_title="Web Crawling Chatbot - ADK",
    page_icon="🕷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stAlert > div {
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # ADK-specific session state
    if "adk_session_service" not in st.session_state:
        st.session_state.adk_session_service = InMemorySessionService()
    
    if "adk_runner" not in st.session_state:
        # Use 'adk_agent' as app_name to match the module/folder name
        st.session_state.adk_runner = Runner(
            agent=root_agent,
            app_name="adk_agent",  # Must match the folder name where agent.py is located
            session_service=st.session_state.adk_session_service
        )
    
    if "adk_user_id" not in st.session_state:
        st.session_state.adk_user_id = "streamlit_user"
    
    if "adk_session_id" not in st.session_state:
        st.session_state.adk_session_id = "session_001"


def ask_agent_with_context(question: str) -> str:
    """
    Ask the agent a question with webpage context using direct LiteLLM.
    Model-agnostic approach that works reliably.
    
    Args:
        question: User's question
        
    Returns:
        Agent's response
    """
    try:
        import litellm
        
        # Get stored content
        content = webpage_storage.get("content", "")
        
        # Check if this is a greeting or general question
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
        is_greeting = question.lower().strip() in greetings
        
        # Build context-aware prompt
        if content and not is_greeting:
            # Include webpage content in the prompt for context-based Q&A
            full_prompt = f"""Answer the following question based ONLY on the provided webpage content.

Webpage Content:
{content[:15000]}

Question: {question}

Please provide a clear, concise answer based only on the information in the webpage content above. If the question cannot be answered from the webpage content, say so."""
        else:
            # For greetings or when no content, just use the question as-is
            if is_greeting:
                full_prompt = f"{question}\n\nRespond briefly and offer to help answer questions about the loaded webpage."
            else:
                full_prompt = question
        
        # Get model configuration
        model_provider = os.getenv("MODEL_PROVIDER", "ollama").lower()
        model_name = os.getenv("MODEL_NAME", "mistral")
        
        # Build model string for LiteLLM
        if model_provider == "ollama":
            model = f"ollama_chat/{model_name}"
            api_base = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
        elif model_provider == "openai":
            model = model_name  # e.g., "gpt-4"
            api_base = None
        elif model_provider == "anthropic":
            model = model_name  # e.g., "claude-3-sonnet-20240229"
            api_base = None
        elif model_provider == "gemini":
            # For Gemini via LiteLLM
            model = f"gemini/{model_name}"
            api_base = None
        else:
            model = f"{model_provider}/{model_name}"
            api_base = None
        
        # Call LiteLLM directly - works with all providers
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": full_prompt}],
            api_base=api_base if api_base else None,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error: {str(e)}\n\nPlease ensure your model provider is running and configured correctly."


def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Title
    st.title("🕷️ Web Crawling Chatbot")
    st.markdown("*Powered by Google ADK Framework (Model-Agnostic)*")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Model Provider Status
        model_provider = os.getenv("MODEL_PROVIDER", "ollama").lower()
        model_name = os.getenv("MODEL_NAME", "mistral")
        
        st.subheader("� Model Configuration")
        
        # Display provider-specific info
        if model_provider == "ollama":
            st.success("🦙 Ollama (Self-hosted)")
            st.caption(f"Model: {model_name}")
            ollama_base = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
            st.caption(f"Endpoint: {ollama_base}")
            st.info("✅ No API key required")
        elif model_provider == "openai":
            st.success("🔵 OpenAI GPT")
            st.caption(f"Model: {model_name}")
            has_key = bool(os.getenv("OPENAI_API_KEY"))
            if has_key:
                st.info("✅ API key configured")
            else:
                st.error("❌ OPENAI_API_KEY not set")
        elif model_provider == "anthropic":
            st.success("🟣 Anthropic Claude")
            st.caption(f"Model: {model_name}")
            has_key = bool(os.getenv("ANTHROPIC_API_KEY"))
            if has_key:
                st.info("✅ API key configured")
            else:
                st.error("❌ ANTHROPIC_API_KEY not set")
        elif model_provider == "gemini":
            st.success("🔴 Google Gemini")
            st.caption(f"Model: {model_name}")
            has_key = bool(os.getenv("GOOGLE_API_KEY"))
            if has_key:
                st.info("✅ API key configured")
            else:
                st.error("❌ GOOGLE_API_KEY not set")
        else:
            st.warning(f"⚙️ {model_provider.upper()}")
            st.caption(f"Model: {model_name}")
        
        st.caption("via LiteLLM + ADK")
        
        # ADK info
        st.subheader("ADK Framework")
        st.success("✅ Google ADK Active")
        if st.session_state.get("adk_session_id"):
            st.caption(f"Session: {st.session_state.adk_session_id[:8]}...")
        
        st.divider()
        
        # Session controls
        st.subheader("Session")
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
        
        if st.button("🔄 Reset All", use_container_width=True):
            st.session_state.chat_history = []
            webpage_storage.clear()
            # Reset session (will be recreated by Runner on next interaction)
            st.session_state.adk_session_id = "session_001"
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📄 Fetch Webpage")
        
        # URL input
        url_input = st.text_input(
            "Enter webpage URL:",
            placeholder="http://localhost:8000/cats_guide.html",
            key="url_field"
        )
        
        # Fetch button
        if st.button("🔍 Fetch Page", type="primary"):
            if url_input:
                with st.spinner("Fetching webpage..."):
                    try:
                        # Directly call the fetch function (bypassing the agent for this step)
                        result = fetch_and_store_webpage(url_input)
                        
                        if result["status"] == "success":
                            st.success(f"✅ Fetched {result['word_count']} words from webpage")
                            st.text_area("Preview", result['content'][:500], height=150)
                        else:
                            st.error(f"❌ Failed to fetch: {result['message']}")
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter a URL")
    
    with col2:
        st.subheader("📊 Status")
        if webpage_storage.get("content"):
            st.metric("Words Loaded", webpage_storage.get("word_count", 0))
            st.metric("URL", "✅ Loaded")
            if webpage_storage.get("url"):
                st.caption(webpage_storage["url"][:50] + "...")
        else:
            st.info("No webpage loaded yet")
    
    # Content preview
    if webpage_storage.get("content"):
        with st.expander("📄 Webpage Content Preview"):
            preview = get_content_preview(webpage_storage["content"], max_chars=1000)
            st.text_area(
                "Content:",
                value=preview,
                height=200,
                disabled=True
            )
    
    st.divider()
    
    # Chat interface
    st.subheader("💬 Ask Questions")
    
    # Display chat history
    if st.session_state.chat_history:
        for i, (role, message) in enumerate(st.session_state.chat_history):
            if role == "user":
                with st.chat_message("user"):
                    st.write(message)
            else:
                with st.chat_message("assistant"):
                    st.write(message)
    
    # Chat input
    if prompt := st.chat_input("Ask a question about the webpage..."):
        if not webpage_storage.get("content"):
            st.warning("⚠️ Please fetch a webpage first before asking questions!")
        else:
            # Add user message to history
            st.session_state.chat_history.append(("user", prompt))
            
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
            
            # Get agent response using direct Ollama
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = ask_agent_with_context(prompt)
                    st.write(response)
                    st.session_state.chat_history.append(("assistant", response))


if __name__ == "__main__":
    main()
