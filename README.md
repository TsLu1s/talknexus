Capstone project in progress - chatbot interface forked from talknexus



# TalkNexus: Ollama Chatbot Multi-Model & RAG Interface

A comprehensive and scalable Chatbot Application that integrates multiple language models through the Ollama API, featuring sophisticated model management, interactive chat interfaces, and RAG (Retrieval-Augmented Generation) capabilities for document analysis.

## 🌟 Key Features

- **Multi-Model Support**: Seamlessly interact with various state-of-the-art Ollama language models including DeepSeek, Llama, Mistral, and 125+ more.
- **Model Management Interface**: Easy-to-use interface for downloading, managing, and switching between different language models.
- **Real-time Chat Interface**:  Clean interface with model-specific chat history and streamed responses.
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

- Python 3.10 or higher
- Ollama API (latest version)
- Streamlit
- 8GB+ RAM (varies based on model size)

**Important Note:** Demo Version is not able to run Ollama API, run the app locally for full feature usability.

## ⚙️ Installation

1. **Clone the Repository**
```bash
git clone https://github.com/TsLu1s/talknexus.git
cd talknexus
```

2. **Set Up Conda Environment**

First, ensure you have Conda installed. Then create and activate a new environment with Python 3.10:

```bash
# Create new environment
conda create -n talknexus_env python=3.10

# Activate the environment
conda activate talknexus_env
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Install Ollama**
   
Visit Ollama API and follow the installation instructions for your operating system.


<div align="left">
   
[![Download Ollama](https://img.shields.io/badge/DOWNLOAD-OLLAMA-grey?style=for-the-badge&labelColor=black)](https://ollama.com/download)

</div>

5. **Start the Application**
```bash
streamlit run navigation.py
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

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See [LICENSE](https://github.com/TsLu1s/talknexus/blob/main/LICENSE) for more information.

## 🔗 Contact 
 
Luis Santos - [LinkedIn](https://www.linkedin.com/in/lu%C3%ADsfssantos/)
# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
