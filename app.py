import asyncio
import sys
import streamlit as st
import os
import time
from typing import Optional
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlite3
from datetime import datetime, timedelta

# Windows asyncio compatibility
if sys.platform.startswith('win') and sys.version_info >= (3, 8):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

class LAWONTIPConfig:
    """Configuration class for LAWONTIP"""
    def __init__(self):
        load_dotenv()
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.database_url = "sqlite:///lawontip_users.db"
        
        # Check for required environment variables
        missing_keys = []
        if not self.google_api_key:
            missing_keys.append("GOOGLE_API_KEY")
        if not self.groq_api_key:
            missing_keys.append("GROQ_API_KEY")
        
        if missing_keys:
            st.error(f"""
            Missing required API keys: {', '.join(missing_keys)}
            
            Please create a .env file in the project root with the following variables:
            GOOGLE_API_KEY=your_google_api_key_here
            GROQ_API_KEY=your_groq_api_key_here
            
            You can get these keys from:
            - Google AI: https://makersuite.google.com/app/apikey
            - Groq: https://console.groq.com/keys
            """)
            st.stop()
        
        # Set environment variables
        os.environ['GOOGLE_API_KEY'] = self.google_api_key

class LAWONTIPDatabaseManager:
    """Database management class for LAWONTIP"""
    def __init__(self, config: LAWONTIPConfig):
        self.Base = declarative_base()
        self.engine = create_engine(config.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

class LAWONTIPStyleManager:
    """CSS styles management for LAWONTIP - Improved Black & White Theme with Better Visibility"""
    
    @staticmethod
    def get_global_styles():
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
        .main > div {
            padding-top: 1rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        
        .stApp {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 30%, #2a2a2a 70%, #1a1a1a 100%);
            min-height: 100vh;
            position: relative;
        }
        
        .stApp::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 80%, rgba(255, 255, 255, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.12) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(255, 255, 255, 0.06) 0%, transparent 50%);
            pointer-events: none;
            z-index: -1;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
        button[title="View fullscreen"] {visibility: hidden;}
        .reportview-container {margin-top: -2em;}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {width: 12px;}
        ::-webkit-scrollbar-track {
            background: rgba(0,0,0,0.9);
            border-radius: 6px;
        }
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(45deg, #ffffff, #e0e0e0);
            border-radius: 6px;
            border: 2px solid rgba(0,0,0,0.9);
        }
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(45deg, #e0e0e0, #ffffff);
        }
        
        /* Improved text visibility */
        .stMarkdown, .stMarkdown p, .stMarkdown div {
            color: rgba(255, 255, 255, 0.95) !important;
            font-weight: 400 !important;
            line-height: 1.6 !important;
        }
        
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            color: #ffffff !important;
            font-weight: 600 !important;
        }
        </style>
        """
    
    @staticmethod
    def get_landing_styles():
        return """
        <style>
        .hero-container {
            background: linear-gradient(145deg, 
                rgba(255, 255, 255, 0.15) 0%, 
                rgba(255, 255, 255, 0.08) 30%, 
                rgba(255, 255, 255, 0.04) 100%);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 30px;
            padding: 4rem 3rem;
            margin: 3rem auto;
            max-width: 1200px;
            text-align: center;
            box-shadow: 
                0 30px 60px rgba(0,0,0,0.9),
                0 0 100px rgba(255, 255, 255, 0.15),
                inset 0 2px 0 rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(25px);
            position: relative;
            overflow: hidden;
        }
        
        .hero-container::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.05) 0%, transparent 70%);
            animation: pulse 4s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.4; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }
        
        .hero-title {
            font-family: 'Playfair Display', serif;
            font-size: 5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 30%, #e0e0e0 70%, #d0d0d0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 1.5rem;
            text-shadow: 0 6px 12px rgba(0,0,0,0.7);
            position: relative;
            z-index: 2;
            letter-spacing: -2px;
        }
        
        .hero-subtitle {
            font-size: 2.2rem;
            background: linear-gradient(90deg, #ffffff 0%, #e0e0e0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 2.5rem;
            font-weight: 600;
            position: relative;
            z-index: 2;
            text-shadow: 0 4px 8px rgba(0,0,0,0.5);
        }
        
        .hero-description {
            font-size: 1.4rem;
            color: rgba(255, 255, 255, 0.95);
            max-width: 800px;
            margin: 0 auto 3.5rem auto;
            line-height: 1.8;
            text-shadow: 0 3px 6px rgba(0,0,0,0.6);
            position: relative;
            z-index: 2;
            font-weight: 400;
        }
        
        .features-container {
            max-width: 1200px;
            margin: 6rem auto 3rem auto;
            padding: 0 2rem;
        }
        
        .features-title {
            font-family: 'Playfair Display', serif;
            text-align: center;
            background: linear-gradient(135deg, #ffffff 0%, #e0e0e0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 4rem;
            text-shadow: 0 4px 8px rgba(0,0,0,0.5);
            letter-spacing: -1px;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 3rem;
            margin-bottom: 5rem;
        }
        
        .feature-card {
            background: linear-gradient(145deg, 
                rgba(255, 255, 255, 0.12) 0%, 
                rgba(255, 255, 255, 0.06) 100%);
            border: 2px solid rgba(255, 255, 255, 0.25);
            border-radius: 25px;
            padding: 3rem 2.5rem;
            text-align: center;
            backdrop-filter: blur(20px);
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
            min-height: 280px;
        }
        
        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
            transition: left 0.6s ease;
        }
        
        .feature-card:hover::before {
            left: 100%;
        }
        
        .feature-card:hover {
            transform: translateY(-10px) scale(1.03);
            background: linear-gradient(145deg, 
                rgba(255, 255, 255, 0.18) 0%, 
                rgba(255, 255, 255, 0.10) 100%);
            box-shadow: 
                0 25px 60px rgba(0,0,0,0.7),
                0 0 40px rgba(255, 255, 255, 0.25);
            border-color: rgba(255, 255, 255, 0.5);
        }
        
        .feature-icon {
            font-size: 4rem;
            margin-bottom: 2rem;
            filter: drop-shadow(0 6px 12px rgba(0,0,0,0.5));
            display: block;
        }
        
        .feature-card h3 {
            background: linear-gradient(135deg, #ffffff 0%, #e0e0e0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 1.6rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            font-family: 'Playfair Display', serif;
            line-height: 1.3;
        }
        
        .feature-card p {
            color: rgba(255, 255, 255, 0.9);
            line-height: 1.8;
            font-size: 1.1rem;
            font-weight: 400;
        }
        
        .footer {
            text-align: center;
            color: rgba(255, 255, 255, 0.7);
            padding: 4rem;
            margin-top: 5rem;
            border-top: 2px solid rgba(255, 255, 255, 0.25);
            font-size: 1rem;
            font-weight: 400;
        }
        
        /* Improved Start Chatting Button Styles */
        .stButton > button {
            background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 50%, #e0e0e0 100%) !important;
            color: #000000 !important;
            padding: 1.5rem 4rem !important;
            border: 3px solid rgba(255, 255, 255, 0.4) !important;
            border-radius: 50px !important;
            font-weight: 800 !important;
            font-size: 1.4rem !important;
            cursor: pointer !important;
            transition: all 0.4s ease !important;
            box-shadow: 
                0 15px 40px rgba(0,0,0,0.7),
                0 8px 25px rgba(255, 255, 255, 0.15) !important;
            text-decoration: none !important;
            display: inline-block !important;
            position: relative !important;
            z-index: 2 !important;
            text-transform: uppercase !important;
            letter-spacing: 1.5px !important;
            width: 100% !important;
            min-height: 70px !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-4px) scale(1.08) !important;
            box-shadow: 
                0 20px 50px rgba(0,0,0,0.9),
                0 12px 35px rgba(255, 255, 255, 0.25) !important;
            background: linear-gradient(135deg, #f0f0f0 0%, #ffffff 50%, #e0e0e0 100%) !important;
            border-color: rgba(255, 255, 255, 0.6) !important;
        }
        </style>
        """
    
    @staticmethod
    def get_chat_styles():
        return """
        <style>
        .chat-container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .chat-header {
            background: linear-gradient(145deg, 
                rgba(255, 255, 255, 0.18) 0%, 
                rgba(255, 255, 255, 0.10) 100%);
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 25px;
            padding: 3rem;
            margin-bottom: 2.5rem;
            text-align: center;
            backdrop-filter: blur(25px);
            box-shadow: 
                0 20px 45px rgba(0,0,0,0.7),
                0 0 40px rgba(255, 255, 255, 0.15);
            position: relative;
            overflow: hidden;
        }
        
        .chat-header::before {
            content: '';
            position: absolute;
            top: -3px;
            left: -3px;
            right: -3px;
            bottom: -3px;
            background: linear-gradient(45deg, #ffffff, #f0f0f0, #e0e0e0, #ffffff);
            border-radius: 25px;
            z-index: -1;
            animation: borderGlow 3s ease-in-out infinite;
        }
        
        @keyframes borderGlow {
            0%, 100% { opacity: 0.4; }
            50% { opacity: 0.8; }
        }
        
        .chat-title {
            font-family: 'Playfair Display', serif;
            background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 50%, #e0e0e0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 1rem;
            text-shadow: 0 4px 8px rgba(0,0,0,0.5);
        }
        
        .chat-subtitle {
            color: rgba(255, 255, 255, 0.95);
            font-size: 1.4rem;
            font-weight: 500;
        }
        
        .input-section {
            background: linear-gradient(145deg, 
                rgba(255, 255, 255, 0.12) 0%, 
                rgba(255, 255, 255, 0.06) 100%);
            border: 2px solid rgba(255, 255, 255, 0.25);
            border-radius: 20px;
            padding: 2.5rem;
            margin-bottom: 2.5rem;
            backdrop-filter: blur(20px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.5);
        }
        
        /* Improved Radio Button Styles */
        .stRadio {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
        }
        
        .stRadio > div {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            gap: 3rem !important;
            margin-bottom: 2rem !important;
            width: 100% !important;
        }
        
        .stRadio > div > label {
            background: linear-gradient(135deg, 
                rgba(255, 255, 255, 0.15) 0%, 
                rgba(255, 255, 255, 0.08) 100%) !important;
            border: 2px solid rgba(255, 255, 255, 0.4) !important;
            padding: 1.2rem 2.5rem !important;
            border-radius: 18px !important;
            color: rgba(255, 255, 255, 0.98) !important;
            transition: all 0.3s ease !important;
            font-weight: 600 !important;
            font-size: 1.2rem !important;
            cursor: pointer !important;
            min-width: 220px !important;
            text-align: center !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
        }
        
        .stRadio > div > label:hover {
            background: linear-gradient(135deg, 
                rgba(255, 255, 255, 0.25) 0%, 
                rgba(255, 255, 255, 0.15) 100%) !important;
            border-color: rgba(255, 255, 255, 0.7) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4) !important;
            color: #ffffff !important;
        }
        
        /* Radio button selected state */
        .stRadio input[type="radio"]:checked + label {
            background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%) !important;
            color: #000000 !important;
            border-color: #ffffff !important;
            font-weight: 700 !important;
            box-shadow: 0 8px 25px rgba(0,0,0,0.5) !important;
        }
        
        /* Fix for radio button text visibility */
        .stRadio label span {
            color: rgba(255, 255, 255, 0.98) !important;
            font-weight: 600 !important;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
        }
        
        .stRadio input[type="radio"]:checked + label span {
            color: #000000 !important;
            font-weight: 700 !important;
            text-shadow: none !important;
        }
        
        /* Additional fixes for radio button container */
        .stRadio div[role="radiogroup"] {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            gap: 3rem !important;
            width: 100% !important;
        }
        
        .stRadio div[role="radiogroup"] > label {
            color: rgba(255, 255, 255, 0.98) !important;
            font-weight: 600 !important;
        }
        
        /* Improved Text Input Styles */
        .stTextInput > div > div > input, .stChatInput > div > div > input {
            background: linear-gradient(145deg, 
                rgba(255, 255, 255, 0.08) 0%, 
                rgba(255, 255, 255, 0.04) 100%) !important;
            border: 3px solid rgba(255, 255, 255, 0.4) !important;
            border-radius: 20px !important;
            color: rgba(255, 255, 255, 0.98) !important;
            padding: 1.5rem 2rem !important;
            font-size: 1.2rem !important;
            transition: all 0.3s ease !important;
            font-weight: 500 !important;
            min-height: 60px !important;
        }
        
        .stTextInput > div > div > input:focus, .stChatInput > div > div > input:focus {
            border-color: #ffffff !important;
            box-shadow: 
                0 0 35px rgba(255, 255, 255, 0.4),
                0 0 60px rgba(255, 255, 255, 0.15) !important;
            background: linear-gradient(145deg, 
                rgba(255, 255, 255, 0.12) 0%, 
                rgba(255, 255, 255, 0.06) 100%) !important;
        }
        
        .stTextInput > div > div > input::placeholder, .stChatInput > div > div > input::placeholder {
            color: rgba(255, 255, 255, 0.7) !important;
            font-weight: 400 !important;
        }
        
        /* Improved Button Styles for Chat */
        .stButton > button {
            background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 50%, #e0e0e0 100%) !important;
            color: #000000 !important;
            border: 3px solid rgba(255, 255, 255, 0.4) !important;
            border-radius: 20px !important;
            padding: 1.2rem 3rem !important;
            font-weight: 700 !important;
            font-size: 1.2rem !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
            text-transform: uppercase !important;
            letter-spacing: 0.8px !important;
            box-shadow: 0 12px 35px rgba(0,0,0,0.5) !important;
            min-height: 60px !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 
                0 18px 45px rgba(0,0,0,0.7),
                0 0 40px rgba(255, 255, 255, 0.25) !important;
            background: linear-gradient(135deg, #f0f0f0 0%, #ffffff 50%, #e0e0e0 100%) !important;
            border-color: rgba(255, 255, 255, 0.6) !important;
        }
        
        /* Improved Chat Message Styles */
        .stChatMessage {
            background: linear-gradient(145deg, 
                rgba(255, 255, 255, 0.10) 0%, 
                rgba(255, 255, 255, 0.05) 100%) !important;
            border: 2px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 20px !important;
            margin-bottom: 2rem !important;
            backdrop-filter: blur(20px) !important;
            box-shadow: 0 8px 25px rgba(0,0,0,0.5) !important;
            transition: all 0.3s ease !important;
            padding: 1.5rem !important;
        }
        
        .stChatMessage:hover {
            border-color: rgba(255, 255, 255, 0.4) !important;
            box-shadow: 0 12px 35px rgba(0,0,0,0.6) !important;
            transform: translateY(-1px) !important;
        }
        
        .stChatMessage [data-testid="chatAvatarIcon-user"] {
            background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%) !important;
            color: #000000 !important;
            border: 2px solid rgba(255, 255, 255, 0.3) !important;
        }
        
        .stChatMessage [data-testid="chatAvatarIcon-assistant"] {
            background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%) !important;
            color: #ffffff !important;
            border: 2px solid rgba(255, 255, 255, 0.4) !important;
        }
        
        .stChatMessage .stMarkdown {
            color: rgba(255, 255, 255, 0.95) !important;
            line-height: 1.7 !important;
            font-size: 1.1rem !important;
            font-weight: 400 !important;
        }
        
        .stChatMessage .stMarkdown p {
            color: rgba(255, 255, 255, 0.95) !important;
            margin-bottom: 1rem !important;
        }
        
        /* Back Button Improved */
        .back-button, .stButton[data-testid="baseButton-secondary"] > button {
            position: fixed !important;
            top: 2rem !important;
            left: 2rem !important;
            background: linear-gradient(135deg, 
                rgba(255, 255, 255, 0.2) 0%, 
                rgba(255, 255, 255, 0.12) 100%) !important;
            border: 3px solid rgba(255, 255, 255, 0.4) !important;
            border-radius: 50px !important;
            padding: 1rem 2.5rem !important;
            color: rgba(255, 255, 255, 0.95) !important;
            text-decoration: none !important;
            backdrop-filter: blur(20px) !important;
            transition: all 0.3s ease !important;
            z-index: 1000 !important;
            font-weight: 600 !important;
            box-shadow: 0 8px 25px rgba(0,0,0,0.5) !important;
            font-size: 1.1rem !important;
        }
        
        .back-button:hover, .stButton[data-testid="baseButton-secondary"] > button:hover {
            background: linear-gradient(135deg, 
                rgba(255, 255, 255, 0.25) 0%, 
                rgba(255, 255, 255, 0.15) 100%) !important;
            border-color: rgba(255, 255, 255, 0.6) !important;
            transform: translateY(-3px) !important;
            box-shadow: 0 12px 35px rgba(0,0,0,0.6) !important;
        }
        
        /* Status Indicator Improved */
        .stStatus {
            background: linear-gradient(145deg, 
                rgba(255, 255, 255, 0.12) 0%, 
                rgba(255, 255, 255, 0.06) 100%) !important;
            border: 2px solid rgba(255, 255, 255, 0.25) !important;
            border-radius: 18px !important;
            backdrop-filter: blur(15px) !important;
            box-shadow: 0 8px 25px rgba(0,0,0,0.4) !important;
        }
        
        .stStatus .stMarkdown {
            color: rgba(255, 255, 255, 0.9) !important;
            font-weight: 500 !important;
        }
        
        /* Chat Input Improvements */
        .stChatInput {
            margin-top: 2rem !important;
        }
        
        .stChatInput > div {
            background: linear-gradient(145deg, 
                rgba(255, 255, 255, 0.08) 0%, 
                rgba(255, 255, 255, 0.04) 100%) !important;
            border: 2px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 25px !important;
            backdrop-filter: blur(15px) !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4) !important;
        }
        </style>
        """

class LAWONTIPApp:
    """Main application class for LAWONTIP"""
    
    def __init__(self):
        self.config = LAWONTIPConfig()
        self.db_manager = LAWONTIPDatabaseManager(self.config)
        self.style_manager = LAWONTIPStyleManager()
        self._initialize_session_state()
        self._configure_page()
    
    def _initialize_session_state(self):
        """Initialize session state variables"""
        if 'page' not in st.session_state:
            st.session_state.page = 'landing'
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'memory' not in st.session_state:
            st.session_state.memory = ConversationBufferWindowMemory(
                k=2, memory_key="chat_history", return_messages=True
            )
    
    def _configure_page(self):
        """Configure Streamlit page"""
        st.set_page_config(
            page_title="LAWONTIP - AI Legal Assistant",
            page_icon="⚖️",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        st.markdown(self.style_manager.get_global_styles(), unsafe_allow_html=True)
    
    def go_to_page(self, page: str):
        """Navigate to a specific page"""
        st.session_state.page = page
        st.rerun()
    
    def render_landing_page(self):
        """Render the landing page"""
        st.markdown(self.style_manager.get_landing_styles(), unsafe_allow_html=True)
        
        # Hero section
        st.markdown("""
        <div class="hero-container">
            <div class="hero-title">⚖️ LAWONTIP</div>
            <div class="hero-subtitle">Your AI Legal Assistant</div>
            <div class="hero-description">
                Get instant legal guidance, document analysis, and answers to your legal questions 
                with advanced AI technology trained on comprehensive Indian legal databases.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # CTA Button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 Start Chatting", key="start_chat", use_container_width=True):
                self.go_to_page('chat')
        
        # Features section
        st.markdown("""
        <div class="features-container">
            <div class="features-title">Why Choose LAWONTIP?</div>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">📚</div>
                    <h3>Comprehensive Legal Research</h3>
                    <p>Access extensive legal databases and get instant answers to complex legal questions with proper citations and references from Indian legal system.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">⚡</div>
                    <h3>24/7 Instant Assistance</h3>
                    <p>Get legal guidance anytime, anywhere. LAWONTIP is always ready to help with your legal questions and scenarios.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔒</div>
                    <h3>Secure & Confidential</h3>
                    <p>Your conversations and documents are protected with enterprise-grade security and complete confidentiality.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🎯</div>
                    <h3>Specialized Knowledge</h3>
                    <p>Trained on extensive Indian legal databases covering criminal law, civil law, corporate law, contracts, and litigation.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Footer
        st.markdown("""
        <div class="footer">
            <p>&copy; 2025 LAWONTIP. All rights reserved. | Not a substitute for professional legal advice.</p>
        </div>
        """, unsafe_allow_html=True)
    
    def _initialize_llm_components(self):
        """Initialize LLM components"""
        if not hasattr(self, 'qa'):
            try:
                embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
                db = FAISS.load_local("my_vector_store", embeddings, allow_dangerous_deserialization=True)
            except Exception as e:
                st.error(f"Could not load vector store: {e}")
                st.stop()
            
            try:
                db_retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 4})
                llm = ChatGroq(groq_api_key=self.config.groq_api_key, model_name="llama3-70b-8192")
                self.qa = ConversationalRetrievalChain.from_llm(
                    llm=llm,
                    memory=st.session_state.memory,
                    retriever=db_retriever,
                    combine_docs_chain_kwargs={'prompt': self._get_prompt_template()}
                )
            except Exception as e:
                st.error(f"Could not initialize LLM components: {e}")
                st.stop()
    
    def _get_prompt_template(self):
        """Get the prompt template"""
        prompt_template = """
        As a legal chatbot specializing in Indian law, provide accurate and concise information based on the user's questions. 
        Focus on relevant context from the knowledge base while avoiding unnecessary details. Your responses should be brief, 
        professional, and contextually relevant. If a question falls outside the given context, rely on your knowledge base 
        to generate an appropriate response. Prioritize the user's query and deliver precise information pertaining to Indian legal system.
        
        CONTEXT: {context}
        CHAT HISTORY: {chat_history}
        QUESTION: {question}
        ANSWER:
        """
        return PromptTemplate(template=prompt_template, input_variables=['context', 'question', 'chat_history'])
    
    def _get_scenario_prompt_template(self):
        """Get the scenario prompt template"""
        scenario_template = """
        You are a legal expert chatbot specializing in Indian law. When a user describes a scenario, analyze it, 
        identify the relevant legal issue, and provide the most applicable law, section, or rule from the Indian legal context. 
        Use the provided context from the knowledge base to support your answer. If the scenario involves exceptions 
        (such as self-defense), explain the relevant law and its application concisely.

        CONTEXT: {context}
        CHAT HISTORY: {chat_history}
        SCENARIO: {question}
        ANSWER:
        """
        return PromptTemplate(template=scenario_template, input_variables=['context', 'question', 'chat_history'])
    
    def reset_conversation(self):
        """Reset conversation history"""
        st.session_state.messages = []
        st.session_state.memory.clear()
        st.rerun()
    
    def render_chat_page(self):
        """Render the chat page"""
        st.markdown(self.style_manager.get_chat_styles(), unsafe_allow_html=True)
        
        # Back button
        if st.button("← Back to Home", key="back_home"):
            self.go_to_page('landing')
        
        # Chat container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Chat header
        st.markdown("""
        <div class="chat-header">
            <div class="chat-title">⚖️ LAWONTIP Chat</div>
            <div class="chat-subtitle">Ask your legal questions or describe your scenario below</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize LLM components
        self._initialize_llm_components()
        
        # Input section
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        
        # Input type selection with improved visibility
        st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h3 style="color: rgba(255, 255, 255, 0.95); font-size: 1.3rem; font-weight: 600; text-align: center; margin-bottom: 1rem;">
                What would you like to do?
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        input_type = st.radio(
            "",
            ("Ask a legal question", "Describe a scenario"),
            horizontal=True,
            key="input_type",
            label_visibility="collapsed"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(f"""
                <div style="color: rgba(255, 255, 255, 0.95); font-size: 1.1rem; line-height: 1.6; font-weight: 400;">
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
        
        # Chat input
        if prompt := st.chat_input("Enter your legal question or scenario here..."):
            # Add user message
            with st.chat_message("user"):
                st.markdown(f"""
                <div style="color: rgba(255, 255, 255, 0.95); font-size: 1.1rem; line-height: 1.6; font-weight: 400;">
                    {prompt}
                </div>
                """, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Generate response
            with st.chat_message("assistant"):
                with st.status("🤔 Analyzing your query...", expanded=True):
                    st.markdown("""
                    <div style="color: rgba(255, 255, 255, 0.9); font-size: 1rem; font-weight: 500;">
                        🔍 Searching legal database...
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(0.5)
                    
                    st.markdown("""
                    <div style="color: rgba(255, 255, 255, 0.9); font-size: 1rem; font-weight: 500;">
                        ⚖️ Analyzing relevant laws...
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(0.5)
                    
                    st.markdown("""
                    <div style="color: rgba(255, 255, 255, 0.9); font-size: 1rem; font-weight: 500;">
                        📝 Preparing response...
                    </div>
                    """, unsafe_allow_html=True)
                    
                    try:
                        # Use appropriate prompt based on input type
                        if input_type == "Describe a scenario":
                            # Update QA chain with scenario prompt
                            self.qa.combine_docs_chain.llm_chain.prompt = self._get_scenario_prompt_template()
                        else:
                            # Use default prompt
                            self.qa.combine_docs_chain.llm_chain.prompt = self._get_prompt_template()
                        
                        result = self.qa.invoke(input=prompt)
                    except Exception as e:
                        st.error(f"Error generating response: {e}")
                        result = {"answer": "I apologize, but I encountered an error while processing your request. Please try again."}
                    
                    # Display response with improved styling
                    st.markdown(f"""
                    <div style="color: rgba(255, 255, 255, 0.95); font-size: 1.1rem; line-height: 1.7; font-weight: 400; padding: 1rem; background: linear-gradient(145deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%); border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.1);">
                        {result["answer"]}
                    </div>
                    """, unsafe_allow_html=True)
            
            st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
        
        # Control buttons with improved spacing and visibility
        st.markdown("<div style='margin-top: 3rem;'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                self.reset_conversation()
        with col2:
            if st.button("📝 New Question", use_container_width=True):
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def run(self):
        """Run the application"""
        if st.session_state.page == 'landing':
            self.render_landing_page()
        elif st.session_state.page == 'chat':
            self.render_chat_page()

# Run the application
if __name__ == "__main__":
    app = LAWONTIPApp()
    app.run()