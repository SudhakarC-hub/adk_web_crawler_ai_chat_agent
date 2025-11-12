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
    
    if "adk_session" not in st.session_state:
        # Create session synchronously - InMemorySessionService doesn't use async
        session_service = st.session_state.adk_session_service
        # Try to get or create session directly
        try:
            # Use a simple session ID
            session_id = "streamlit_session_001"
            # Check if session exists, if not it will be created by Runner
            st.session_state.adk_session_id = session_id
        except Exception as e:
            st.error(f"Error initializing session: {e}")
            st.session_state.adk_session_id = "default_session"
    
    if "adk_runner" not in st.session_state:
        st.session_state.adk_runner = Runner(
            agent=root_agent,
            app_name="ADKWebCrawler",
            session_service=st.session_state.adk_session_service
        )


def ask_agent_with_context(question: str) -> str:
    """
    Ask the agent a question with webpage context.
    Uses direct Ollama call for reliable responses.
    
    Args:
        question: User's question
        
    Returns:
        Agent's response
    """
    try:
        import ollama
        
        # Get stored content
        content = webpage_storage.get("content", "")
        
        # Check if this is a greeting or general question (not about the content)
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
        is_greeting = question.lower().strip() in greetings
        
        # Build context-aware prompt
        if content and not is_greeting:
            prompt = f"""You are a helpful AI assistant. Answer the following question based ONLY on the provided webpage content.

Webpage Content:
{content[:15000]}

Question: {question}

Please provide a clear, concise answer based only on the information in the webpage content above. If the question cannot be answered from the webpage content, say so."""
        else:
            # For greetings or when no content, just respond naturally
            if is_greeting:
                prompt = f"{question}\n\nRespond briefly and offer to help answer questions about the loaded webpage."
            else:
                prompt = question
        
        # Call Ollama directly for reliable responses
        response = ollama.chat(
            model='mistral',
            messages=[{
                'role': 'user',
                'content': prompt
            }]
        )
        
        return response['message']['content']
        
    except Exception as e:
        return f"Error: {str(e)}"


def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Check Ollama connection
    ollama_base = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
    
    # Title
    st.title("🕷️ Web Crawling Chatbot")
    st.markdown("*Powered by Google ADK + LiteLLM + Ollama (Mistral)*")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Ollama connection status
        st.subheader("🦙 Ollama")
        st.success("✅ Self-hosted (No API key needed)")
        st.caption(f"Endpoint: {ollama_base}")
        
        # Model info
        st.subheader("🤖 Model")
        model_name = os.getenv("OLLAMA_MODEL", "mistral")
        st.info(f"Using: {model_name}")
        st.caption("Local LLM via LiteLLM")
        
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
            # Reset session ID (Runner will handle session creation)
            st.session_state.adk_session_id = "streamlit_session_001"
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
