# Lawon_tip
# LAWONTIP: AI Legal Assistant

![Python 3.12](https://img.shields.io/badge/Python-3.10-brightgreen.svg) [![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](#)  

LAWONTIP is an AI-powered legal assistant designed to provide comprehensive legal information and guidance. The chatbot utilizes RAG (Retrieval-Augmented Generation) architecture, advanced language models, and embeddings to retrieve and generate contextually relevant answers from a comprehensive Indian legal document corpus.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Architecture](#architecture)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)

## Introduction

LAWONTIP aims to assist users by providing accurate and concise legal information based on Indian legal documents including the Indian Penal Code, Companies Act, Copyright Rules, and other relevant legal frameworks. The chatbot retrieves relevant context from the knowledge base to answer user queries efficiently.

## Features

- **Modern UI**: Beautiful, responsive interface with dark theme
- **Conversational Interface**: Natural chat-based interaction for legal queries
- **Dual Modes**: Ask legal questions or describe scenarios for analysis
- **Comprehensive Knowledge**: Covers Indian Penal Code, Civil Law, Corporate Law, and more
- **Real-time Responses**: Fast, accurate responses using advanced LLMs
- **Context Awareness**: Maintains conversation history for better responses
- **Source Citations**: Provides relevant legal references and citations

## Architecture

The architecture of LAWONTIP includes the following components:

1. **Document Loader**: Loads legal documents from a directory of PDF files
2. **Text Splitter**: Splits documents into manageable chunks for embedding
3. **Embeddings**: Uses Google Generative AI Embeddings to transform text into vector representations
4. **Vector Store**: Utilizes FAISS to store and retrieve document embeddings
5. **LLM**: Uses the Groq API (Llama 3) to generate responses based on retrieved documents and user queries
6. **Memory**: Maintains a conversation buffer to provide context in conversations
7. **Web Interface**: Streamlit-based responsive web application

## Setup and Installation

### Prerequisites

- Python 3.10 or higher
- API keys for Google AI and Groq

### Installation Steps

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/LAWONTIP.git
cd LAWONTIP
```

2. **Set Up Virtual Environment**
```bash
# Using conda
conda create -p venv python=3.10
conda activate venv

# Or using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Set Up Environment Variables**

Create a `.env` file in the project root directory:
```bash
# Google AI API Key (for embeddings)
# Get it from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_google_api_key_here

# Groq API Key (for LLM responses)
# Get it from: https://console.groq.com/keys
GROQ_API_KEY=your_groq_api_key_here
```

5. **Prepare Legal Documents**

The project includes a pre-built vector store, but if you want to rebuild it:
```bash
python ingestion.py
```

## Usage

### Running the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

### Using the Chat Interface

1. **Landing Page**: Start by exploring the features and clicking "Start Chatting"
2. **Chat Interface**: 
   - Choose between "Ask a legal question" or "Describe a scenario"
   - Type your legal query or describe your situation
   - Get instant, accurate legal guidance
3. **Navigation**: Use the back button to return to the landing page
4. **Chat Management**: Clear chat history or start new questions as needed

## Troubleshooting

### Common Issues

1. **Missing API Keys**
   - Ensure your `.env` file exists and contains valid API keys
   - Check that the API keys are active and have sufficient credits

2. **Vector Store Issues**
   - If you get vector store errors, ensure the `my_vector_store` directory exists
   - Rebuild the vector store using `python ingestion.py`

3. **Import Errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility (3.10+ recommended)

4. **Memory Issues**
   - The application uses FAISS for vector storage which requires sufficient RAM
   - Consider reducing the number of documents if you encounter memory issues

### Getting Help

If you encounter issues:
1. Check the console output for error messages
2. Ensure all API keys are valid and have sufficient credits
3. Verify that all dependencies are correctly installed
4. Check that the vector store files exist in the `my_vector_store` directory

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

LAWONTIP is designed to provide legal information and guidance but is not a substitute for professional legal advice. Always consult with qualified legal professionals for specific legal matters.



