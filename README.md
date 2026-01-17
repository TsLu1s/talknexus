# TalkNexus: Ollama Chatbot Multi-Model & RAG Interface

A comprehensive and scalable Chatbot Application that integrates multiple language models through the Ollama API, featuring sophisticated model management, interactive chat interfaces, and RAG (Retrieval-Augmented Generation) capabilities for document analysis.

## 🌟 Key Features

- **Multi-Model Support**: Seamlessly interact with various state-of-the-art Ollama language models including DeepSeek, Llama, Mistral, and 125+ more.
- **Model Management Interface**: Easy-to-use interface for downloading, managing, and switching between different language models.
- **Real-time Chat Interface**: Clean interface with model-specific chat history and streamed responses.
- **Conversation History Management**: Save, load, and manage chat conversations with automatic titling and organized storage for easy access to previous interactions.
- **RAG-Powered Document Analysis**: Advanced document processing system supporting PDF analysis with multiple embedding models for context-aware document querying and intelligent responses.
- **Experiment Management**: Save, load, and track different document analysis configurations with customizable retrieval settings for reproducible results.
- **Responsive Design**: Modern, responsive UI with animated components and intuitive navigation.

## 📽️ TalkNexus APP Video

https://github.com/user-attachments/assets/46b20f63-505e-424c-a93a-df60ded20051

## 👏 Acknowledgments

* [Ollama](https://ollama.com/)
* [Langchain](https://langchain.com/)
* [Streamlit](https://streamlit.io/)  

## Streamlit Demo APP

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://talknexus.streamlit.app/)

## 📋 Prerequisites

- Python 3.11 or higher
- Ollama API (latest version)
- Poetry (Python package manager)
- 8GB+ RAM (varies based on model size)

**Important Note:** Demo Version is not able to run Ollama API, run the app locally for full feature usability.

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/TsLu1s/talknexus.git
cd talknexus
```

### 2. Install Python 3.11

**macOS (using pyenv):**
```bash
# Install pyenv if not already installed
brew install pyenv

# Install Python 3.11
pyenv install 3.11

# Set Python 3.11 for this project
pyenv local 3.11
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv
```

**Windows:**

Download and install Python 3.11 from [python.org](https://www.python.org/downloads/)

### 3. Install Poetry
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Verify installation:
```bash
poetry --version
```

> **Note:** You may need to add Poetry to your PATH. Follow the instructions shown after installation or add this to your shell config:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```

### 4. Configure Poetry to Use Python 3.11
```bash
poetry env use python3.11
```

### 5. Install Dependencies
```bash
poetry install
```

### 6. Install Ollama

Visit Ollama and follow the installation instructions for your operating system.

<div align="left">
   
[![Download Ollama](https://img.shields.io/badge/DOWNLOAD-OLLAMA-grey?style=for-the-badge&labelColor=black)](https://ollama.com/download)

</div>

### 7. Start the Application
```bash
poetry run streamlit run app.py
```

Or activate the Poetry shell first:
```bash
poetry shell
streamlit run app.py
```

## 💻 Usage & Architecture

### Home Page
- Explore the Ollama model ecosystem with detailed model cards
- View comprehensive information about model capabilities and specializations:
  - Language Models, Specialized Models, Task-Specific Models, Domain-Specific Models...
- Access quick reference for hardware requirements
- Find links to essential documentation and resources

### Model Management
1. Navigate to the "Language Models Management" section
2. Select and download desired models from the available list
3. Monitor installation progress and system requirements
4. Manage installed models through the interface

### Chat Interface
1. Select a model from the dropdown menu
2. Enter your message in the chat input
3. View real-time responses in the chat window
4. Switch between models as needed
5. Access conversation history
   - Start new conversations
   - Load previous conversations
   - Continue ongoing conversations
   - Delete unwanted conversations

### RAG Chat Interface

1. Upload PDF documents for analysis
2. Select embedding model and language model
3. Configure retrieval settings with customizable chunk sizes and parent documents
4. Save and manage experiments for reproducibility
5. Ask questions about your documents
6. Receive context-aware responses based on document content

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See [LICENSE](https://github.com/TsLu1s/talknexus/blob/main/LICENSE) for more information.

## 🔗 Contact 
 
Luis Santos - [LinkedIn](https://www.linkedin.com/in/lu%C3%ADsfssantos/)