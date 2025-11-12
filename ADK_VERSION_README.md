# Web Crawling Chatbot - ADK Version

A Streamlit-based web crawling chatbot powered by Google ADK framework and Ollama (self-hosted Mistral LLM).

## 🎯 Features

- **Web Scraping**: Fetch and parse webpage content
- **Context-Aware Chat**: Ask questions about fetched webpages
- **Self-Hosted LLM**: Uses Ollama with Mistral model (no API keys required)
- **ADK Framework**: Built with Google Agent Development Kit for proper agent structure
- **Streamlit UI**: Clean, modern web interface

## 🏗️ Architecture

- **Framework**: Google ADK (Agent Development Kit)
- **LLM**: Self-hosted Ollama with Mistral model
- **Frontend**: Streamlit
- **Web Scraping**: BeautifulSoup4 + Requests

## 📋 Prerequisites

1. **Python 3.9+** (3.10+ recommended)
2. **Ollama** installed and running
   ```bash
   # Install Ollama: https://ollama.ai
   ollama pull mistral
   ollama serve
   ```

## 🚀 Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd WebCrawlerADKChatAgent
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows
```

### 3. Install dependencies
```bash
pip install -r ADK_VERSION_requirements.txt
```

### 4. Set environment variables
```bash
export OLLAMA_API_BASE=http://localhost:11434
```

## 📂 Project Structure

```
WebCrawlerADKChatAgent/
├── adk_agent/                      # ADK agent module
│   ├── __init__.py                 # Exports root_agent
│   ├── agent.py                    # Agent definition with tools
│   └── .env.example                # Environment configuration template
├── adk_app.py                      # Streamlit frontend
├── web_utils.py                    # Web scraping utilities
├── config.py                       # Application configuration
├── cats_guide.html                 # Sample HTML page for testing (cat care)
├── dogs_guide.html                 # Sample HTML page for testing (dog care)
├── ADK_VERSION_requirements.txt    # Python dependencies
├── quick_start_adk.sh              # Quick start setup script
├── verify_setup.py                 # Setup verification script
└── ADK_VERSION_README.md           # This file
```

## 🎮 Usage

### Running the Streamlit App

```bash
# Make sure Ollama is running
ollama serve

# Activate virtual environment
source venv/bin/activate

# Set environment variable
export OLLAMA_API_BASE=http://localhost:11434

# Run the app
streamlit run adk_app.py
```

Access the app at: **http://localhost:8501**

### Using the ADK CLI

The agent is compatible with ADK command-line tools:

```bash
# Run agent in interactive mode
export OLLAMA_API_BASE=http://localhost:11434
adk run adk_agent

# Launch web interface
adk web
```

### Testing with Sample Pages

Sample HTML pages are included for testing:

```bash
# Start local HTTP server (in a separate terminal)
cd /path/to/WebCrawlerADKChatAgent
python3 -m http.server 8000

# Pages will be available at:
# http://localhost:8000/cats_guide.html
# http://localhost:8000/dogs_guide.html
```

**In the Streamlit app, you can now fetch either:**
- Cat care guide: `http://localhost:8000/cats_guide.html`
- Dog care guide: `http://localhost:8000/dogs_guide.html`

## 🔧 Configuration

### Environment Variables

Create a `.env` file or export these variables:

```bash
# Ollama API endpoint (required)
OLLAMA_API_BASE=http://localhost:11434

# Optional: Model selection (default: mistral)
OLLAMA_MODEL=mistral
```

### Model Configuration

Edit `config.py` to adjust:
- `MAX_WORDS`: Maximum words to extract from webpages (default: 5000)
- `DEFAULT_MODEL_NAME`: Ollama model to use

## 📝 How It Works

### 1. Webpage Fetching
- User enters a URL in the Streamlit interface
- `fetch_and_store_webpage()` tool fetches and parses the content
- Content is cleaned and stored in memory
- Preview is displayed to the user

### 2. Question Answering
- User asks a question in the chat interface
- Agent receives the question with webpage context
- Ollama (Mistral) generates answer based on stored content
- Response is displayed in the chat

### 3. ADK Integration
The agent uses Google ADK framework components:
- **Agent**: Core LLM agent with tool capabilities
- **Tools**: `fetch_and_store_webpage` and `get_content_summary`
- **Session Management**: InMemorySessionService for conversation state
- **Runner**: Executes agent with proper session handling

## 🛠️ Key Files

### `adk_agent/agent.py`
Defines the ADK agent with:
- **Model**: LiteLLM wrapper for Ollama
- **Tools**: Webpage fetching and content retrieval
- **Instructions**: System prompt for agent behavior

### `adk_app.py`
Streamlit frontend with:
- URL input and fetch functionality
- Chat interface for Q&A
- Session state management
- Direct Ollama calls for chat (hybrid approach)

### `web_utils.py`
Web scraping utilities:
- `fetch_webpage_content()`: Fetches and cleans HTML
- `get_content_preview()`: Generates content preview

## 🔍 Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Verify mistral model is installed
ollama list

# Pull mistral if needed
ollama pull mistral
```

### Python Version Warnings
The app works with Python 3.9 but you may see warnings. For best experience:
```bash
# Upgrade to Python 3.10+
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### ADK Session Warnings
App name mismatch warnings are harmless - the app uses a hybrid approach with direct Ollama calls for reliability.

## 🧪 Testing

### Verify Setup
```bash
python verify_setup.py
```

### Test with Sample Page
```bash
# Start HTTP server
python3 -m http.server 8000

# In the Streamlit app, fetch:
# http://localhost:8000/cats_guide.html
# http://localhost:8000/dogs_guide.html
```

## 📊 Performance

- **Webpage Fetch**: ~1-3 seconds (depends on page size)
- **Chat Response**: ~2-5 seconds (depends on Ollama performance)
- **Memory Usage**: ~500MB (includes Streamlit + dependencies)

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Add support for more LLM models
- Implement RAG with vector database
- Add authentication and user management
- Support multiple concurrent sessions
- Add more sophisticated web scraping (JavaScript rendering)

## 📜 License

MIT License - feel free to use and modify for your projects.

## 🙏 Acknowledgments

- **Google ADK**: Agent Development Kit framework
- **Ollama**: Self-hosted LLM infrastructure
- **Streamlit**: Web app framework
- **BeautifulSoup**: HTML parsing library

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Verify Ollama is running: `ollama list`
3. Check terminal output for detailed error messages

---

**Built with ❤️ using Google ADK and Ollama**

