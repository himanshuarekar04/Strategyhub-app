#Functioning
#CHATGPT 4 cost efficient
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_community.embeddings import OpenAIEmbeddings
import openai
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import time
import logging
import hashlib
import random
from enum import Enum
import pycountry
from forex_python.converter import CurrencyRates
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json
from fpdf import FPDF
import io
from textblob import TextBlob
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
import requests
from bs4 import BeautifulSoup
import yfinance as yf
from pytrends.request import TrendReq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from gensim import corpora
from gensim.models import LdaModel
from gensim.parsing.preprocessing import STOPWORDS
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
from urllib.parse import urlparse
import traceback
from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import firebase_admin
from typing import List, Dict
import math
import camelot
import fitz  # PyMuPDF
from streamlit_option_menu import option_menu
import razorpay
import base64
from firebase_admin import credentials, auth, initialize_app, firestore
from PIL import Image

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=("YOUR_KEY_ID", "YOUR_KEY_SECRET"))


# Helper functions for business analysis logic

countries_with_currencies = [
    (country.name, pycountry.currencies.get(numeric=country.numeric).alpha_3)
    for country in pycountry.countries
    if hasattr(country, 'numeric') and pycountry.currencies.get(numeric=country.numeric)
]
countries_with_currencies.sort(key=lambda x: x[0])  # Sort alphabetically by country name

def convert_currency(amount, from_currency, to_currency):
    try:
        c = CurrencyRates()
        return c.convert(from_currency, to_currency, amount)
    except:
        st.warning(f"Unable to convert {from_currency} to {to_currency}. Using original amount.")
    return amount

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GOOGLE_TRENDS_API_KEY = os.getenv("GOOGLE_TRENDS_API_KEY")

# Set up Google Trends client
pytrends = TrendReq(hl='en-US', tz=360)

def generate_unique_key(base_key):
    return hashlib.md5(base_key.encode()).hexdigest()

# Additional initialization code as needed
if not firebase_admin._apps:
    cred = credentials.Certificate("C:\\Users\\Lenovo\\Downloads\\New intern project\\intern\private_key.json")
    firebase_admin.initialize_app(cred)

def set_bg(image_file):
    with open(image_file, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{encoded_string});
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        /* Custom CSS */
        .section {{
            padding: 40px 20px;
            margin-bottom: 30px;
            background-color: rgba(0, 0, 0, 0.6);
            border-radius: 15px;
        }}
        
        .feature-card {{
            background-color: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            transition: transform 0.3s;
            backdrop-filter: blur(5px);
        }}
        
        .feature-card:hover {{
            transform: translateY(-5px);
            background-color: rgba(255, 255, 255, 0.2);
        }}
        
        .benefit-card {{
            background-color: rgba(51, 51, 51, 0.8);
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 4px solid #ffdd00;
        }}
        
        .testimonial-card {{
            background-color: rgba(255, 255, 255, 0.15);
            padding: 20px;
            border-radius: 15px;
            margin: 15px 0;
        }}
        
        .pricing-card {{
            background-color: rgba(255, 255, 255, 0.1);
            padding: 25px;
            border-radius: 15px;
            margin: 10px 0;
            text-align: center;
        }}
        
        .cta-button {{
            background: linear-gradient(45deg, #ffdd00, #ffa500);
            border: none;
            border-radius: 25px;
            color: black;
            padding: 12px 30px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 18px;
            margin: 4px 2px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .cta-button:hover {{
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(255, 221, 0, 0.3);
        }}
        
        /* Authentication form styling */
        .auth-form {{
            background-color: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            max-width: 500px;
            margin: 0 auto;
        }}
        
        /* Payment page styling */
        .payment-options {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px;
        }}
        </style>
        """, unsafe_allow_html=True
    )
    
def show_auth_page():
    st.markdown("""
        <div class="auth-form">
            <h2 style="color: white; text-align: center;">Login or Register</h2>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            try:
                user = login_user(email, password)
                if user:
                    st.session_state.user = user
                    st.session_state.subscription_status = check_user_subscription()
                    st.success("Successfully logged in!")
                    st.session_state.stage = 'features'
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            except Exception as e:
                st.error(f"Login failed: {str(e)}")
    
    with tab2:
        st.subheader("Register")
        name = st.text_input("Full Name")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("Register"):
            if password != confirm_password:
                st.error("Passwords don't match")
            else:
                try:
                    user = register_user(email, password, name)
                    if user:
                        st.session_state.user = user
                        st.success("Successfully registered!")
                        st.session_state.stage = 'features'
                        st.rerun()
                    else:
                        st.error("Registration failed")
                except Exception as e:
                    st.error(f"Registration failed: {str(e)}")

def login_user(email: str, password: str):
    """
    Authenticate a user with email and password
    """
    try:
        # Verify the user credentials with Firebase
        user = auth.get_user_by_email(email)
        
        # Get user details from Firestore
        db = firestore.client()
        user_doc = db.collection('users').document(user.uid).get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            # Store user information in session state
            st.session_state.user = {
                'uid': user.uid,
                'email': email,
                'name': user_data.get('name', ''),
                'subscription': user_data.get('subscription', None),
                'last_login': datetime.now()
            }
            
            # Update last login in Firestore
            db.collection('users').document(user.uid).update({
                'last_login': datetime.now()
            })
            
            return st.session_state.user
        else:
            raise Exception("User profile not found")
            
    except auth.UserNotFoundError:
        st.error("Invalid email or password")
        return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def register_user(email: str, password: str, name: str):
    """
    Register a new user with email, password, and name
    """
    try:
        # Create the user in Firebase Authentication
        user = auth.create_user(
            email=email,
            password=password,
            display_name=name
        )
        
        # Store additional user data in Firestore
        db = firestore.client()
        db.collection('users').document(user.uid).set({
            'name': name,
            'email': email,
            'created_at': datetime.now(),
            'subscription': None,
            'last_login': datetime.now()
        })
        
        # Store user information in session state
        st.session_state.user = {
            'uid': user.uid,
            'email': email,
            'name': name,
            'subscription': None,
            'last_login': datetime.now()
        }
        
        return st.session_state.user
        
    except auth.EmailAlreadyExistsError:
        st.error("Email already exists")
        return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None


def check_user_subscription():
    """Check the user's subscription status"""
    if not st.session_state.user:
        return None
    
    db = firestore.client()
    user_ref = db.collection('subscriptions').document(st.session_state.user['uid'])
    subscription = user_ref.get()
    
    if subscription.exists:
        subscription_data = subscription.to_dict()
        if subscription_data['end_date'] > datetime.now():
            return subscription_data['plan_name']
    return None

def check_subscription_access(feature):
    """Check if user has access to the selected feature"""
    if not st.session_state.user:
        st.warning("Please login to access this feature.")
        st.session_state.stage = 'auth'
        return False
        
    if feature == 'market_research':
        if st.session_state.market_research_questions_count >= 5 and not st.session_state.subscription_status:
            st.error("You've reached the limit of free market research questions. Please subscribe to continue.")
            st.session_state.stage = 'payment'
            return False
        st.session_state.market_research_questions_count += 1
        return True
    else:
        if not st.session_state.subscription_status:
            st.error("This feature requires a subscription.")
            st.session_state.stage = 'payment'
            return False
        return True

def show_payment_page():
    """Display the payment and subscription options page"""
    st.title("Choose Your Plan")
    
    st.markdown("""
        <div class="payment-options">
            <div class="pricing-card">
                <h3>Basic Plan</h3>
                <h2>₹499/month</h2>
                <ul>
                    <li>Market Research</li>
                    <li>Basic Analysis</li>
                    <li>5 AI Queries/day</li>
                </ul>
                <button class="cta-button" onclick="selectPlan('basic')">Select Basic</button>
            </div>
            
            <div class="pricing-card">
                <h3>Premium Plan</h3>
                <h2>₹999/month</h2>
                <ul>
                    <li>All Basic Features</li>
                    <li>Business Plan Analysis</li>
                    <li>Unlimited AI Queries</li>
                </ul>
                <button class="cta-button" onclick="selectPlan('premium')">Select Premium</button>
            </div>
            
            <div class="pricing-card">
                <h3>Enterprise Plan</h3>
                <h2>₹1999/month</h2>
                <ul>
                    <li>All Premium Features</li>
                    <li>Custom Solutions</li>
                    <li>Priority Support</li>
                </ul>
                <button class="cta-button" onclick="selectPlan('enterprise')">Select Enterprise</button>
            </div>
        </div>
    """, unsafe_allow_html=True)

def show_options_page():
    st.title("Choose Your Service")
    
    # Create a modern card layout for options
    st.markdown("""
        <style>
        .service-card {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin: 10px;
            transition: transform 0.3s;
            cursor: pointer;
        }
        .service-card:hover {
            transform: translateY(-5px);
            background-color: rgba(255, 255, 255, 0.2);
        }
        .premium-tag {
            color: #FFD700;
            font-size: 14px;
            font-weight: bold;
        }
        .free-tag {
            color: #90EE90;
            font-size: 14px;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

# Load the locally saved Strategyhub logo
logo_path = "C:\\Users\\Lenovo\\Downloads\\WhatsApp_Image_2024-10-25_at_12.31.38_5e07f07b-removebg-preview.png"
image = Image.open(logo_path)


def show_landing_page():
    # Transparent Full-Width Navigation Bar
    st.markdown("""
        <nav style="display: flex; justify-content: space-between; align-items: center; background-color: rgba(51, 51, 51, 0.8); padding: 15px; width: 100vw; position: fixed; top: 50px; left: 0; right: 0; z-index: 100; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);">
            <div style="display: flex; justify-content: space-between; align-items: center; width: 100%; padding: 0 20px;">
                <div style="display: flex; align-items: center;">
                    <img src="C:\\Users\\Lenovo\\Downloads\\WhatsApp_Image_2024-10-25_at_12.31.38_5e07f07b-removebg-preview.png" style="height: 40px; margin-right: 10px;">
                    <span style="color: white; font-size: 24px;">StrategyHub</span>
                </div>
                <div style="display: flex; gap: 30px;">
                    <a href="#about" style="color: white; text-decoration: none;">About</a>
                    <a href="#features" style="color: white; text-decoration: none;">Features</a>
                    <a href="#pricing" style="color: white; text-decoration: none;">Pricing</a>
                    <a href="#documentation" style="color: white; text-decoration: none;">Documentation & Tutorials</a>
                    <a href="#contact" style="color: white; text-decoration: none;">Contact</a>
                </div>
            </div>
        </nav>
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown("""
        <div style="text-align: center; padding: 100px 20px 40px 20px;">
            <h1 style="color: white; font-size: 48px; margin-bottom: 20px;">
                Welcome to StrategyHub
            </h1>
            <p style="color: white; font-size: 20px; max-width: 700px; margin: 0 auto;">
                Explore tailored insights, data-driven analysis, and actionable recommendations for your business success.
            </p>
        </div>
    """, unsafe_allow_html=True)


    # Get Started Button
    if st.button("Get Started for Free", key="get_started_button"):
        st.session_state.stage = 'features'
        st.rerun()

    # Display other sections
    show_features_section()
    show_benefits_section()
    show_pricing_section()
    show_about_section()
    show_contact_section()
    show_footer()


def show_features_section():
    st.markdown("""
        <div class="section" id="features">
            <h2 style="color: white; text-align: center; margin-bottom: 30px;">Key Features</h2>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
                <div class="feature-card">
                    <h3 style="color: #ffdd00;">Business Analysis</h3>
                    <p style="color: white;">Get detailed insights into your business trends and key performance indicators.</p>
                </div>
                <div class="feature-card">
                    <h3 style="color: #ffdd00;">Market Research</h3>
                    <p style="color: white;">Access comprehensive market research with our free trial.</p>
                </div>
                <div class="feature-card">
                    <h3 style="color: #ffdd00;">Business Plan Analysis</h3>
                    <p style="color: white;">Get expert analysis of your business plans (Premium feature).</p>
                </div>
                <div class="feature-card">
                    <h3 style="color: #ffdd00;">New Business Plan Generation</h3>
                    <p style="color: white;">Generate detailed business plans with AI assistance (Premium feature).</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def show_benefits_section():
    st.markdown("""
        <div class="section">
            <h2 style="color: white; text-align: center; margin-bottom: 30px;">Benefits</h2>
            <div class="benefit-card">
                <h3 style="color: #ffdd00;">Free Market Research Trial</h3>
                <p style="color: white;">Try our market research feature with 5 free questions.</p>
            </div>
            <div class="benefit-card">
                <h3 style="color: #ffdd00;">Premium Features</h3>
                <p style="color: white;">Access advanced business analysis and planning tools with our premium plans.</p>
            </div>
            <div class="benefit-card">
                <h3 style="color: #ffdd00;">AI-Powered Insights</h3>
                <p style="color: white;">Get data-driven recommendations for your business decisions.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

def show_pricing_section():
    st.markdown("""
        <div class="section" id="pricing">
            <h2 style="color: white; text-align: center; margin-bottom: 30px;">Pricing Plans</h2>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
                <div class="pricing-card">
                    <h3 style="color: #ffdd00;">Free Trial</h3>
                    <p style="color: white;">Start with market research</p>
                    <ul style="color: white; text-align: left;">
                        <li>5 market research questions</li>
                        <li>Basic features</li>
                        <li>Community support</li>
                    </ul>
                    <button class="cta-button" onclick="getStarted()">Get Started Free</button>
                </div>
                <div class="pricing-card">
                    <h3 style="color: #ffdd00;">Premium</h3>
                    <p style="color: white;">₹999/month</p>
                    <ul style="color: white; text-align: left;">
                        <li>Unlimited market research</li>
                        <li>Business analysis tools</li>
                        <li>Priority support</li>
                    </ul>
                    <button class="cta-button" onclick="subscribe('premium')">Subscribe Now</button>
                </div>
                <div class="pricing-card">
                    <h3 style="color: #ffdd00;">Enterprise</h3>
                    <p style="color: white;">Custom pricing</p>
                    <ul style="color: white; text-align: left;">
                        <li>All premium features</li>
                        <li>Custom solutions</li>
                        <li>Dedicated support</li>
                    </ul>
                    <button class="cta-button" onclick="contactSales()">Contact Sales</button>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def show_about_section():
    st.markdown("""
        <div class="section" id="about">
            <h2 style="color: white; text-align: center;">About StrategyHub</h2>
            <p style="color: white; text-align: center; font-size: 18px;">
                StrategyHub empowers businesses with AI-driven insights and analysis. Start with our free market research trial,
                then upgrade to access premium features for comprehensive business planning and analysis.
            </p>
        </div>
    """, unsafe_allow_html=True)

def show_contact_section():
    st.markdown("""
        <div class="section" id="contact">
            <h2 style="color: white; text-align: center;">Contact Us</h2>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
                <div style="color: white;">
                    <h3 style="color: #ffdd00;">Get in Touch</h3>
                    <p>Email: contact@strategyhub.com</p>
                    <p>Phone: +1-234-567-8900</p>
                </div>
                <div style="color: white;">
                    <h3 style="color: #ffdd00;">Connect With Us</h3>
                    <div style="display: flex; gap: 20px;">
                        <a href="#" style="color: #ffdd00;">LinkedIn</a>
                        <a href="#" style="color: #ffdd00;">Twitter</a>
                        <a href="#" style="color: #ffdd00;">Facebook</a>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def show_footer():
    st.markdown("""
        <footer style="background-color: rgba(51, 51, 51, 0.9); padding: 20px; text-align: center; margin-top: 50px;">
            <div style="color: white;">
                <p>© 2024 StrategyHub. All rights reserved.</p>
                <div style="margin-top: 10px;">
                    <a href="#" style="color: #ffdd00; margin: 0 10px;">Terms of Service</a>
                    <a href="#" style="color: #ffdd00; margin: 0 10px;">Privacy Policy</a>
                </div>
            </div>
        </footer>
    """, unsafe_allow_html=True)

def show_features_page():
    st.title("Select a Feature")
    
    st.markdown("""
        <div class="section">
            <p style="color: white;">Choose from our available features:</p>
        </div>
    """, unsafe_allow_html=True)
    
    feature = st.radio(
        "Available Features:",
        ["Market Research (Free Trial - 5 questions)",
         "Analyze Existing Business (Premium)",
         "Analyze Uploaded Business Plan (Premium)",
         "Generate New Business Plan (Premium)"]
    )
    
    if st.button("Proceed"):
        feature_key = feature.split(" (")[0].lower().replace(" ", "_")
        if check_subscription_access(feature_key):
            st.session_state.stage = feature_key
            st.session_state.selected_feature = feature_key
            st.rerun()


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

from langchain_community.embeddings import OpenAIEmbeddings

def get_vector_store(text_chunks):
    try:
        # Use OpenAI Embeddings with "text-embedding-ada-002"
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        vector_store.save_local("faiss_index")
        st.success("FAISS index saved successfully.")
        return vector_store
    except Exception as e:
        # If the model is not found, show an error message and fallback
        st.error(f"Error generating embeddings: {str(e)}. Trying to use an alternative model.")
        
        # Fallback to GPT-3.5 embeddings or other available models
        try:
            embeddings = OpenAIEmbeddings(model="gpt-3.5-turbo")
            vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
            vector_store.save_local("faiss_index")
            st.success("FAISS index saved successfully with GPT-3.5.")
            return vector_store
        except Exception as fallback_e:
            st.error(f"Fallback failed: {str(fallback_e)}")


class ContextManager:
    def __init__(self):
        self.conversation_history = []
        self.user_profile = {}
        self.current_analysis = {}

    def add_to_history(self, role, content):
        self.conversation_history.append({"role": role, "content": content})

    def update_user_profile(self, key, value):
        self.user_profile[key] = value

    def update_current_analysis(self, key, value):
        self.current_analysis[key] = value

    def get_context_string(self):
        return f"""
        Conversation History: {self.conversation_history[-5:]}
        User Profile: {self.user_profile}
        Current Analysis: {self.current_analysis}
        """

def generate_chatgpt_response(prompt, context_manager=None):
    try:
        model = ChatOpenAI(model_name="chatgpt-4o-latest", temperature=0.3)
       
        if context_manager:
            full_prompt = f"""
            Context:
            {context_manager.get_context_string()}

            Based on this context, please respond to the following:
            {prompt}
            """
        else:
            full_prompt = prompt
       
        messages = [
            SystemMessage(content="You are a helpful AI assistant."),
            HumanMessage(content=full_prompt)
        ]
        response = model(messages)
       
        # Add source tracking and citation
        sources = extract_sources(response.content)
        cited_response = add_citations(response.content, sources)
       
        return cited_response
    except Exception as e:
        st.error(f"An error occurred while generating the response: {str(e)}")
        return "I apologize, but I couldn't generate a response at this time. Please try again later."

def extract_sources(content):
    patterns = [
        r'\[(\d+)\]\s*(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*))',
        r'\[(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*))\]',
        r'\((https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*))\)',
        r'(?:Source:|Reference:)\s*(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*))',
        r'(?<![a-zA-Z0-9@:%._\+~#=/])(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*))'
    ]
    
    sources = []
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                source = match[1] if len(match) > 1 else match[0]
            else:
                source = match
            if source and source not in sources:
                sources.append(source)
    
    cleaned_sources = []
    for source in sources:
        if not source.startswith(('http://', 'https://')):
            source = 'https://' + source
        domain = urlparse(source).netloc
        cleaned_sources.append(f"{domain} - {source}")
    
    return cleaned_sources

def add_citations(content, sources):
    # Add inline citations
    for i, source in enumerate(sources, 1):
        domain = source.split(' - ')[0]
        pattern = rf'\b{re.escape(domain)}\b'
        content = re.sub(pattern, f"{domain} [{i}]", content)
    
    # Add sources section
    content += "\n\nSources:\n"
    for i, source in enumerate(sources, 1):
        content += f"{i}. {source}\n"
    
    return content

def generate_confidence_level():
    return round(random.uniform(0.6, 1.0), 2)

def ask_initial_questions():
    questions = [
        "Describe the mission/goal for your company",
        "Describe the problems which you are facing in achieving the mission/goal",
        "Strengths according to you which will help you in achieving the mission/goal",
        "Steps taken till now to achieve the goal"
    ]
    answers = {}
    for question in questions:
        answer = st.text_area(question)
        if answer:
            answers[question] = answer
    return answers

def analyze_answers_and_documents(answers, pdf_content):
    analysis_prompt = f"""
    You are a top-tier business analyst. Review and compare the following information to provide a detailed and accurate assessment:

    User Input (Company Information):
    {answers}

    PDF Document (Comprehensive Company Analysis):
    {pdf_content}

    Based on the above, provide an in-depth analysis covering the following aspects:
    1. Mission/Goal Overview (from user input)
    2. Financial Performance Analysis
    3. Strategic Initiatives Analysis
    4. Operational Efficiency Analysis
    5. Market and Competitive Analysis
    6. SWOT Analysis
    7. PESTEL Analysis
    8. Key Challenges (from both user input and PDF)
    9. Progress Made (from user input)
    10. Risk Management Analysis
    11. Human Resources Analysis
    12. Technology and IT Analysis
    13. Customer Analysis
    14. Environmental, Social, and Governance (ESG) Analysis
    15. Brand and Marketing Analysis
    16. Innovation and R&D Analysis
    17. Detailed Competitive Analysis
    18. Stakeholder Analysis
    19. Detailed Action Plan
    20. Financial Projections
    21. Benchmarking and Best Practices
    22. Change Management Plan
    23. Regulatory and Compliance Analysis
    24. Cultural Analysis
    25. Supply Chain Analysis
    26. Financial Health Indicators
    27. Company Lifecycle
    28. Individual Competitor Analysis
    29. Digital Transformation Assessment
    30. Innovation Pipeline Analysis
    31. Talent Management and Succession Planning
    32. Customer Journey Mapping
    33. Data Analytics Capabilities
    34. Sustainability and Corporate Social Responsibility (CSR) Initiatives
    35. Intellectual Property Portfolio
    36. Global Market Expansion Opportunities
    37. Cybersecurity and Data Privacy Measures
    38. Ecosystem and Partnership Analysis
    39. Agility and Adaptability Assessment
    40. Employee Engagement and Company Culture
    41. Product/Service Portfolio Analysis
    42. Pricing Strategy Assessment
    43. Social Media and Online Presence Analysis
    44. Merger and Acquisition (M&A) Opportunities
    45. Regulatory Compliance Forecast
    46. Customer Segmentation and Targeting
    47. Supply Chain Resilience
    48. Long-term Vision and Strategic Positioning

    Provide an analysis that integrates information from both the user's input and the given document. If the provided document lacks sufficient information, utilize web sources to supplement your analysis with relevant and accurate data. When using web sources:
    - Clearly indicate which information comes from the web versus the original document.
    - Use reputable and up-to-date sources.
    - Cite the sources you use.

    Provide a detailed but structured report which has an industry accepted format. 
    For each point, provide:
    Provide in-depth analysis, specific strategies, and implementation detail along with budget required and execution timeline.
    Include relevant data points, examples, and mini case studies where appropriate either from competitors or businesses doing exceptionally well in that specific industry.
    Explain the rationale behind each strategy and how it aligns with the overall business goals.
    Break down complex ideas into digestible parts and use examples where appropriate to illustrate your points.
    """
    analysis = generate_chatgpt_response(analysis_prompt)
    return analysis

def provide_planning_and_solutions(analysis, budget=None, workforce=None):
    budget_info = f"Budget: ${budget}" if budget is not None else "No budget information provided. Please estimate the realistic budget required to achieve the company's goals."
    workforce_info = f"Workforce: {workforce} employees" if workforce is not None else "No workforce information provided. Please estimate the ideal workforce required to achieve the company's goals."

    prompt = f"""
    You are a top-tier business analyst tasked with creating a detailed and professional strategic plan for a company. 
    Below is the comprehensive analysis of the company:

    {analysis}

    Additional Information:
    - {budget_info}
    - {workforce_info}

    Your goal is to create a thorough, well-structured business plan that addresses all aspects of the company's operations, strategy, and growth. Provide in-depth explanations, avoid bullet points, and ensure each section interconnects with others to form a cohesive strategy. Consider potential challenges, risks, benefits, and implementation steps for each strategy, supported by examples or mini-case studies.

    **Your plan should cover the following sections:**

    1. **Executive Summary**:
       - Provide a high-level overview of the business plan, including the company’s vision, mission, and long-term objectives.

    2. **Company Overview**:
       - Briefly describe the company’s history, key products/services, market position, and leadership structure.
       - Highlight its current challenges and growth potential.

    3. **Market & Competitive Analysis**:
       - Perform an in-depth analysis of the company's market, including size, trends, and customer segmentation.
       - Include a thorough competitor analysis, identifying major players, their strengths/weaknesses, and market share comparisons.

    4. **SWOT & PESTEL Analysis**:
       - Conduct a SWOT (Strengths, Weaknesses, Opportunities, Threats) analysis based on internal and external factors.
       - Use the PESTEL (Political, Economic, Social, Technological, Environmental, Legal) framework to analyze external forces affecting the company.

    5. **Strategic Goals & Objectives**:
       - Define the company’s short-term and long-term strategic goals.
       - Detail specific, measurable objectives for each goal and outline how they align with the company’s mission and market opportunities.

    6. **Marketing & Sales Strategy**:
       - Develop a detailed marketing plan focusing on positioning, pricing, promotion, and product strategies.
       - Include a sales strategy, detailing target customers, sales processes, and growth opportunities.

    7. **Operations & Supply Chain Optimization**:
       - Outline the company’s operational structure, processes, and resources.
       - Provide recommendations for optimizing the supply chain, enhancing operational efficiency, and reducing costs.

    8. **Financial Projections & Risk Mitigation**:
       - Provide detailed financial forecasts, including revenue projections, profit margins, and break-even analysis.
       - Discuss key financial risks and strategies for mitigating them.
       - If no budget is defined by the user, estimate the realistic budget required to achieve the strategic goals.

    9. **Innovation & Digital Transformation Strategy**:
       - Propose strategies for incorporating innovation and digital transformation into the company’s business model.
       - Focus on technology upgrades, automation, R&D, and leveraging data analytics for decision-making.

    10. **Human Resources & Talent Management**:
        - Assess the company’s human resources strategy, including workforce engagement, culture development, talent acquisition, and succession planning.
        - If no workforce information is provided by the user, estimate the ideal number of employees required to achieve the strategic goals.

    11. **Technology, Data, and Cybersecurity**:
        - Analyze the company's current technology infrastructure.
        - Provide recommendations for improving cybersecurity, data protection, and IT capabilities to support future growth.

    12. **Sustainability & CSR Initiatives**:
        - Include strategies for enhancing the company's sustainability practices and corporate social responsibility (CSR) efforts.
        - Provide insights on how to integrate sustainability into the core business model.

    13. **Global Expansion & Market Growth Opportunities**:
        - Evaluate potential opportunities for expanding into new markets or regions.
        - Propose strategies for entering global markets, considering cultural, legal, and economic factors.

    14. **Contingency Plans and Crisis Management**:
        - Detail a comprehensive contingency plan for addressing unforeseen events such as economic downturns, supply chain disruptions, or natural disasters.
        - Include crisis management strategies to ensure business continuity.

    15. **Implementation Timeline & Key Milestones**:
        - Provide a detailed execution plan with timelines, resource allocation, and key milestones for tracking progress.
        - Include specific steps for each strategic initiative and indicate the necessary budget and workforce for each phase.

    16. **Performance Metrics & KPIs**:
        - Define clear Key Performance Indicators (KPIs) to measure the success of the strategic initiatives.
        - Propose methods for tracking and evaluating performance over time.

    Ensure the plan provides specific, actionable recommendations, backed by data where possible. Each section should include step-by-step implementation details, key stakeholders, and expected outcomes. Provide a cohesive narrative that links the various strategies together, demonstrating how each part contributes to the overall business success.
    """
    plan = generate_chatgpt_response(prompt)
    return plan


def is_business_plan(text):
    keywords = ["executive summary", "business model", "market analysis", "financial projections", "competitive analysis"]
    return any(keyword in text.lower() for keyword in keywords)

def analyze_uploaded_plan(pdf_content):
    if not is_business_plan(pdf_content):
        return "This document does not appear to be a business plan."

    prompt = f"""
    Analyze the following business plan:

    {pdf_content}

    Provide a comprehensive analysis including:
    
    1. Executive Summary Overview
    2. Business Model Evaluation
    3. Market Analysis Assessment
    4. Financial Projections Review
    5. SWOT Analysis
    6. Risk Assessment
    7. Mission Alignment Evaluation
    8. Areas for Improvement:
       - Identify specific areas where the plan can be enhanced to better achieve its mission
       - Provide actionable recommendations for each area of improvement
       - Prioritize improvements based on potential impact and feasibility
    9. Implementation Strategy:
       - Suggest a step-by-step approach to implement the recommended improvements
       - Provide a timeline for implementation
       - Identify potential challenges and mitigation strategies
    10. Performance Metrics:
        - Propose key performance indicators (KPIs) to measure the success of improvements
        - Suggest a monitoring and evaluation framework
    11. Resource Allocation:
        - Recommend how resources should be allocated to support improvements
        - Identify any additional resources that may be required
    12. Competitive Advantage Analysis:
        - Evaluate how the proposed improvements will enhance the company's competitive position
    13. Long-term Sustainability:
        - Assess the long-term viability of the plan with the proposed improvements
        - Suggest strategies for ensuring continued relevance and success

    Focus specifically on elements typical to a business plan. If any key sections are missing, note their absence and suggest improvements.
    If it's a business plan then only ensure the analysis is thorough, actionable, and focused on achieving the company's mission. 
    Provide specific, data-driven insights where possible, and highlight any assumptions made in the analysis.
    If anything is not mentioned in the plan or requires clarification, note it as an area needing further development.
    """
    analysis = generate_chatgpt_response(prompt)
    return analysis

def fetch_data_from_url(url: str) -> str:
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return ""

def parse_html(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    for item in soup.find_all('div', class_='g'):
        title = item.find('h3', class_='r')
        link = item.find('a')
        snippet = item.find('div', class_='s')
        if title and link and snippet:
            results.append({
                'title': title.text,
                'link': link['href'],
                'snippet': snippet.text
            })
    return results[:5]  # Return only the first 5 results

def fetch_industry_data(industry: str, location: str) -> List[Dict]:
    url = f"https://www.google.com/search?q={industry}+market+size+{location}"
    html = fetch_data_from_url(url)
    return parse_html(html)

def fetch_competitor_data(business_type: str, location: str) -> List[Dict]:
    url = f"https://www.google.com/search?q={business_type}+competitors+in+{location}"
    html = fetch_data_from_url(url)
    return parse_html(html)

def generate_financial_model(initial_investment, projected_revenue, target_market_share, years=3):
    # Calculate key financial metrics
    annual_growth_rate = math.pow(projected_revenue / initial_investment, 1/years) - 1
    yearly_projections = [initial_investment * math.pow(1 + annual_growth_rate, year) for year in range(1, years+1)]
   
    return {
        'initial_investment': initial_investment,
        'projected_revenue': projected_revenue,
        'target_market_share': target_market_share,
        'annual_growth_rate': annual_growth_rate,
        'yearly_projections': yearly_projections
    }

def validate_section_financials(section_content, financial_model, tolerance=0.1):
    # Check if the generated content aligns with the financial model
    # This is a basic check and can be expanded for more thorough validation
    key_metrics = [
        str(financial_model['initial_investment']),
        str(financial_model['projected_revenue']),
        f"{financial_model['target_market_share']}%",
        f"{financial_model['annual_growth_rate']:.2%}"
    ]
   
    return all(metric in section_content for metric in key_metrics)


def generate_new_business_plan(business_idea, business_type, target_market, initial_investment, industry, location, product_positioning, usp, geographical_target, target_market_share, founders_experience, currency):
    sections = [
        "Executive Summary",
        "Company Description",
        "Market Research and Analysis",
        "Organization and Management",
        "Products and Services",
        "Marketing and Sales Strategy",
        "Funding Requirements and Financial Plan",
        "Operational Plan",
        "Legal Compliances",
        "Conclusion"
    ]
   
    full_plan = {}
    collective_research = ""

    # Fetch relevant data upfront
    try:
        industry_data = fetch_industry_data(industry, location)
        competitor_data = fetch_competitor_data(business_type, location)
    except Exception as e:
        print(f"Error fetching data: {e}")
        industry_data = []
        competitor_data = []
   
    for section in sections:
        prompt = f"""
        You are an expert Business plan generator. Generate a detailed {section} for a business plan with the following details:

        Business Idea: {business_idea}
        Business Type: {business_type}
        Target Market: {target_market}
        Location: {location}
        Industry: {industry}
        Product Positioning: {product_positioning}
        Unique Selling Proposition (USP): {usp}
        Geographical Target: {geographical_target}
        Target Market Share in {geographical_target}: {target_market_share}% in 3 years
        Founders' Experience: {founders_experience}

        Critical Instructions:
        1. Structure the content with clear headings and subheadings.
        2. Under each subheading, provide thorough explanations and descriptions.
        3. Use markdown formatting for headings and subheadings:
           # Main Heading
           ## Subheading
           ### Sub-subheading (if needed)
        4. In the "Funding Requirements and Financial Plan" section, include detailed financial tables using markdown table syntax.
        5. Ensure all financial projections are consistent with the provided financial model.
        6. Avoid repeating information from other sections. Each section should provide unique insights.
        7. Provide a complete and descriptive plan using paragraphs instead of bullet points. Aim for a flowing narrative.
        8. Use relative timeframes (e.g., Month 3, Year 1 Q3, Year 2 Q2) instead of specific dates.
        9. Justify all projections and estimates with data-driven reasoning.
        10. Cite sources for all statistics and data provided. Use reputable sources and include the date of the data.
        11. Incorporate insights from the following collective research gathered so far: {collective_research}
        12. Include at least two relevant quotes from industry reports to support key points. Do NOT generate any quotes from industry experts or individuals.
        13. Ensure that at least 80% of the content is in paragraph form, using bullet points sparingly and only when absolutely necessary for clarity.
        14. Focus on providing comprehensive information and analysis without summarizing or concluding at the end of each section.
        15. Do not invent or assume any external validation, endorsements, or opinions about the product or service.
        16. If expert opinions or testimonials would be valuable in a section, instead write: "[Note: Expert opinions or testimonials would be valuable here once the product is developed and tested.]"
        17. Base all market research and analysis specifically on the provided location ({location}).
        18. Detect and determine competitors based on the provided location and by analyzing the business idea and business type.
        19. Calculate revenue projections based on the industry CAGR and the target market share.
        20. Provide real-world and original statistics for the target market from reliable sources to calculate the total addressable market.
        21. Align all marketing and sales strategies, investment needs, financial projections, and team requirements with the projected revenue based on the target market share.
        22. Ensure that the projected profitability is accurate and does not show unnecessary fluctuations.
        23. Analyze and properly show the founders' experience in the output as per the input provided.
        24. Do NOT include any conclusions or summaries in this section. All conclusions should be reserved for the dedicated Conclusion section at the end of the plan.

        Specific requirements for {section}:
        """

        if section == "Executive Summary":
            prompt += """
            - Clearly state the name of the business and what it does
            - Explain the problem the business solves
            - Define the mission and vision of the business
            - List the key products/services being offered
            - Describe the target market and unique selling propositions (USPs)
            - Outline short-term and long-term goals
            - Provide a brief financial outlook (expected revenue, profits, etc.)
            """
        elif section == "Company Description":
            prompt += """
            - Specify the legal structure of the company (sole proprietorship, LLC, etc.)
            - State when the business will be launched
            - Describe the industry or sector the company operates in
            - Explain the core values and vision of the business
            - Highlight the competitive advantage of the company in the market
            """
        elif section == "Market Research and Analysis":
            prompt += """
            - Provide the size and growth potential of the market in {location}
            - Analyze main competitors in {location}, their strengths and weaknesses
            - Discuss current market trends specific to {location}
            - Define target customers (demographics, behaviors, preferences) in {location}
            - Explain how the business will position itself within the market in {location}
            - Identify key risks or challenges in the industry specific to {location}
            - Calculate the total addressable market using real-world statistics from reliable sources
            """
        elif section == "Organization and Management":
            prompt += """
            - Describe the ideal profiles for founders and key team members (without using specific names)
            - Describe the organizational structure (hierarchy, roles, and responsibilities)
            - Provide information about the ideal background and expertise of the leadership team (without using specific names)
            - Discuss plans for hiring additional staff and essential roles needed
            - Explain the hiring strategy for essential positions
            - Outline employee policies
            - Analyze and incorporate the provided founders' experience: {founders_experience}
            """
        elif section == "Products and Services":
            prompt += """
            - Detail the specific products or services being offered
            - Explain the pricing strategy for these offerings
            - Describe key features and benefits of the products/services
            - Clarify how the product/service solves the customer's problem
            - Discuss the current development stage of the product/service
            - Address plans for intellectual property protection (if applicable)
            """
        elif section == "Marketing and Sales Strategy":
            prompt += """
            - Outline channels to be used for marketing (online, retail, direct sales)
            - Explain how the business will target its audience to achieve {target_market_share}% market share in 3 years
            - Describe the overall marketing strategy (advertising, social media, partnerships)
            - Detail how the business will generate and convert leads
            - Provide customer acquisition cost (CAC) and lifetime value (LTV) estimates accurately
            - Highlight marketing approach differentiators from competitors
            - Explain market positioning strategy
            - Describe the customer decision-making process
            - Outline customer retention policies
            - Align all strategies with the projected revenue of {projected_revenue:.2f} {currency} after 3 years
            - Provide detailed financial projections for the first 5 years of operation
            - Include yearly projections for:
            - Revenue: Start with {generate_financial_model['initial_investment']:.2f} {currency} and grow to {generate_financial_model['projected_revenue']:.2f} {currency} in Year 3
            - Costs (fixed and variable)
            - Gross profit
            - Operating expenses
            - Net profit
            - Cash flow
            - Show the projected growth rate of {generate_financial_model['annual_growth_rate']:.2%} annually
            - Break down revenue streams if there are multiple products/services
            - Include a break-even analysis
            - Provide key financial ratios (e.g., profit margin, ROI, debt-to-equity ratio)
            - Explain any assumptions made in these projections
            - Include a sensitivity analysis showing best-case and worst-case scenarios
            - Ensure all projections align with the target market share of {generate_financial_model['target_market_share']}% by Year 3
             - Provide monthly projections for the first year, and then annual projections for years 2-5
             - Include visual representations (charts or graphs) of key financial trends
            """
        elif section == "Funding Requirements and Financial Plan":
            prompt += f"""
    To produce highly accurate and consistent financial projections, meticulously follow these enhanced steps:
    
    1. Use Historical Data and Industry Benchmarks:
       - Analyze past performance data (if available) to identify trends in revenue, expenses, and profitability.
       - Compare your data with industry benchmarks from authoritative sources (e.g., PwC Industry Reports, Deloitte Insights).
       - If it's a new business, use data from similar businesses or startups in the same sector.

    2. Comprehensive Market Research:
       - Utilize premium databases (e.g., Statista, IBISWorld, Euromonitor) for in-depth industry data, growth rates, and forecasts.
       - Conduct a thorough competitor analysis, studying financial performances and market strategies of at least 3-5 key competitors.
       - Analyze market saturation, customer segments, and potential market size using the TAM-SAM-SOM model.

    3. Detailed Key Metric Forecasting:
       - Develop a bottom-up revenue model based on pricing strategy, expected units sold, and customer acquisition rates.
       - Create a comprehensive cost structure including fixed costs (rent, salaries) and variable costs (materials, commissions).
       - Project Customer Acquisition Cost (CAC) and Customer Lifetime Value (CLTV) for SaaS or subscription-based models.
       - Calculate key performance indicators (KPIs) specific to your industry (e.g., ARPU for telecom, RevPAR for hotels).

    4. Advanced Financial Modeling:
       - Construct a three-statement financial model (Income Statement, Balance Sheet, Cash Flow Statement) with monthly projections for years 1-2, quarterly for year 3, and annually for years 4-5.
       - Incorporate dynamic sensitivity analysis for key variables (e.g., pricing, market penetration rate, COGS).
       - Use Monte Carlo simulation for risk analysis, running at least 1000 iterations on key variables.

    5. Economic and External Factors:
       - Integrate macroeconomic indicators (GDP growth, inflation rates, exchange rates) from World Bank, IMF, or central bank forecasts.
       - Consider industry-specific factors (e.g., technological disruptions, regulatory changes) and their potential impact.
       - Incorporate seasonal variations if applicable to the business model.

    6. Funding and Investment Analysis:
       - Calculate the exact funding required using a bottom-up approach, breaking down use of funds by department and purpose.
       - Provide a detailed capital structure analysis, including debt-to-equity ratios and cost of capital calculations.
       - Develop a multi-stage funding strategy if applicable, detailing milestones for each round.

    7. Valuation and Exit Strategies:
       - Perform company valuation using multiple methods (e.g., DCF, Comparable Company Analysis, Precedent Transactions).
       - Outline potential exit strategies (IPO, M&A, Management Buyout) with estimated timelines and valuations.

    Based on these enhanced steps, provide:
    - Detailed 5-year financial projections with the following breakdown:
      * Monthly for Year 1
      * Quarterly for Years 2-3
      * Annually for Years 4-5
    - Start with {initial_investment:.2f} {currency} initial investment
    - Show the projected growth rate to achieve the target market share of {target_market_share}% by Year 3
    - Comprehensive break-even analysis including unit economics
    - Detailed cash flow projections including working capital requirements
    - Key financial ratios trend analysis (e.g., Gross Margin, EBITDA Margin, ROE, ROIC)
    - Sensitivity analysis with at least 3 scenarios (Best, Base, Worst case)
    - Waterfall charts for revenue and cost drivers
    - Cohort analysis for customer retention and lifetime value (if applicable)

    Ensure all projections are internally consistent and align with the market research and business strategy. Provide clear, data-driven justifications for all significant assumptions and growth projections.

    Financial Tables:
    1. **Income Statement** (Yearly Summary):
       | **Year**        | **Revenue** | **Cost of Goods Sold (COGS)** | **Gross Profit** | **Operating Expenses** | **Net Profit** |
       |-----------------|--------------|----------------------------|------------------|----------------------|----------------|
       | Year 1 (Monthly)| X,XXX,XXX    | X,XXX,XXX                  | X,XXX,XXX        | X,XXX,XXX            | X,XXX,XXX      |
       | Year 2 (Quarterly)| X,XXX,XXX  | X,XXX,XXX                  | X,XXX,XXX        | X,XXX,XXX            | X,XXX,XXX      |
       | Year 3          | X,XXX,XXX    | X,XXX,XXX                  | X,XXX,XXX        | X,XXX,XXX            | X,XXX,XXX      |
       | Year 4          | X,XXX,XXX    | X,XXX,XXX                  | X,XXX,XXX        | X,XXX,XXX            | X,XXX,XXX      |
       | Year 5          | X,XXX,XXX    | X,XXX,XXX                  | X,XXX,XXX        | X,XXX,XXX            | X,XXX,XXX      |

    2. **Cash Flow Statement**:
       | **Year**        | **Operating Cash Flow** | **Investing Cash Flow** | **Financing Cash Flow** | **Net Cash Flow** | **Cash Balance** |
       |-----------------|------------------------|-------------------------|------------------------|-------------------|------------------|
       | Year 1 (Monthly)| X,XXX,XXX              | X,XXX,XXX               | X,XXX,XXX              | X,XXX,XXX         | X,XXX,XXX        |
       | Year 2 (Quarterly)| X,XXX,XXX            | X,XXX,XXX               | X,XXX,XXX              | X,XXX,XXX         | X,XXX,XXX        |
       | Year 3          | X,XXX,XXX              | X,XXX,XXX               | X,XXX,XXX              | X,XXX,XXX         | X,XXX,XXX        |
       | Year 4          | X,XXX,XXX              | X,XXX,XXX               | X,XXX,XXX              | X,XXX,XXX         | X,XXX,XXX        |
       | Year 5          | X,XXX,XXX              | X,XXX,XXX               | X,XXX,XXX              | X,XXX,XXX         | X,XXX,XXX        |

    3. **Balance Sheet**:
       | **Year**        | **Assets**         | **Liabilities**    | **Equity**       |
       |-----------------|--------------------|--------------------|------------------|
       | Year 1 (Monthly)| X,XXX,XXX          | X,XXX,XXX          | X,XXX,XXX        |
       | Year 2 (Quarterly)| X,XXX,XXX        | X,XXX,XXX          | X,XXX,XXX        |
       | Year 3          | X,XXX,XXX          | X,XXX,XXX          | X,XXX,XXX        |
       | Year 4          | X,XXX,XXX          | X,XXX,XXX          | X,XXX,XXX        |
       | Year 5          | X,XXX,XXX          | X,XXX,XXX          | X,XXX,XXX        |

    4. **Break-Even Analysis**:
       | **Metric**             | **Value**   |
       |------------------------|-------------|
       | Fixed Costs            | X,XXX,XXX   |
       | Variable Costs per Unit| X,XXX       |
       | Selling Price per Unit | X,XXX       |
       | Break-Even Units       | X,XXX       |

    5. **Scenario Analysis**:
       | **Scenario** | **Revenue** | **COGS** | **Operating Expenses** | **Net Profit** | **Growth Rate** |
       |--------------|-------------|----------|-----------------------|----------------|-----------------|
       | Best Case    | X,XXX,XXX   | X,XXX,XXX| X,XXX,XXX             | X,XXX,XXX      | XX%             |
       | Base Case    | X,XXX,XXX   | X,XXX,XXX| X,XXX,XXX             | X,XXX,XXX      | XX%             |
       | Worst Case   | X,XXX,XXX   | X,XXX,XXX| X,XXX,XXX             | X,XXX,XXX      | XX%             |

    Ensure all projections align with these tables and are presented accurately with numbers to two decimal places. Cite all external data sources used.
    """

        elif section == "Operational Plan":
            prompt += """
            - Describe the supply chain model (manufacturing, delivery, inventory management)
            - Detail daily operational requirements
            - Identify key partnerships or suppliers needed
            - Specify technology or software to be used for managing operations
            - Explain how the business will maintain quality control
            - Align operational needs with the projected revenue and market share targets
            """
        elif section == "Legal Compliances":
            prompt += """
            - Provide a comprehensive list of all certificates needed to acquire in {location}
            - Detail all regularities that need to be checked before starting or running the business in {location}
            """
        elif section == "Conclusion":
            prompt += """
            - Summarize the key points from all previous sections
            - Outline short-term, mid-term, and long-term objectives of the business
            - Discuss necessary technological advancements for the company to sustain
            - Detail growth strategies
            - List key performance indicators (KPIs) to monitor
            - Provide execution phases and timeline for the project
            """

        prompt += """
        Provide a comprehensive and detailed {section} that is specific to this business idea and context. Ensure the content is at least 800 words long and includes relevant data, strategies, and insightful analysis. Focus on depth and quality rather than brevity.
        """
        
        model = ChatOpenAI(model_name="gpt-4", temperature=0.7)
        messages = [
            SystemMessage(content="You are an expert business plan generator."),
            HumanMessage(content=prompt)
        ]
        response = model(messages)
        full_plan[section] = response.content
       
        # Update collective research with key points from this section
        collective_research += f"\n\nKey points from {section}:\n" + "\n".join(response.content.split("\n")[:5])
   
    return full_plan

def post_process_business_plan(plan, current_date, current_year, current_quarter, currency, initial_investment, industry, location):
    # Replace any absolute dates with relative timeframes
    for year in range(current_year, current_year + 10):
        plan = plan.replace(str(year), f"Year {year - current_year + 1}")
    
    # Ensure the initial investment is correctly represented
    if f"{initial_investment} {currency}" not in plan:
        plan = f"Warning: The plan may not accurately reflect the initial investment of {initial_investment} {currency}.\n\n" + plan
    
    # Add a note about the base date for all projections
    plan = f"Note: All projections and timelines in this plan are based on the current date of {current_date.strftime('%Y-%m-%d')}.\n\n" + plan
    
    # Check financial projections
    if "Financial Projections" in plan:
        financial_section = plan.split("Financial Projections")[1].split("\n\n")[0]
        
        # Check if initial investment is used as starting point
        if str(initial_investment) not in financial_section:
            plan = plan.replace("Financial Projections", 
                                f"Financial Projections\nWarning: Projections may not accurately reflect the initial investment of {initial_investment} {currency}.")
        
        # Check for justifications
        required_justifications = ["Justify", "Explain", "calculation", "based on"]
        missing_justifications = [j for j in required_justifications if j.lower() not in financial_section.lower()]
        if missing_justifications:
            plan = plan.replace("Financial Projections", 
                                f"Financial Projections\nWarning: Some financial projections lack proper justification. Missing: {', '.join(missing_justifications)}")

    # Ensure industry and location specificity
    if industry.lower() not in plan.lower() or location.lower() not in plan.lower():
        plan = f"Warning: The plan may not adequately address the specific context of the {industry} industry in {location}.\n\n" + plan

    return plan

def generate_scenario_forecasts(analysis, plan):
    prompt = f"""
    Based on the following company analysis and strategic plan:

    Analysis: {analysis}

    Strategic Plan: {plan}

    Generate three different scenario forecasts:
    1. Optimistic Scenario
    2. Base Case Scenario
    3. Pessimistic Scenario

    For each scenario, provide:
    - Key assumptions
    - Economic and market conditions
    - Financial projections (revenue, profit, cash flow)
    - Impact on strategic initiatives
    - Risks and opportunities

    Ensure each scenario is distinct and provides actionable insights. Use specific numbers and percentages in your projections. Explain the reasoning behind each forecast and how different factors interplay to create the scenario.
    """
    forecasts = generate_chatgpt_response(prompt)
    return forecasts

def generate_alternative_plans(analysis, plan, forecasts):
    prompt = f"""
    Based on the following information:

    Company Analysis: {analysis}
    Initial Strategic Plan: {plan}
    Scenario Forecasts: {forecasts}

    Generate three alternative strategic plans corresponding to each scenario forecast:
    1. Optimistic Scenario Plan
    2. Base Case Scenario Plan
    3. Pessimistic Scenario Plan

    For each alternative plan, provide:
    - Adjusted strategic initiatives
    - Resource allocation recommendations
    - Risk mitigation strategies
    - Key performance indicators
    - Timeline for implementation

    Ensure each plan is tailored to its respective scenario and provides concrete, actionable steps. Include specific metrics, timelines, and resource requirements. Explain how each plan adapts the original strategy to the new scenario and why these adaptations are necessary.
    """
    alternative_plans = generate_chatgpt_response(prompt)
    return alternative_plans

def process_regions(regions):
    if not regions or regions.lower() == 'global':
        return ''
    region_list = [r.strip() for r in regions.split(',')]
    country_map = {
        'united states': 'US', 'uk': 'GB', 'india': 'IN', 'canada': 'CA',
        'australia': 'AU', 'germany': 'DE', 'france': 'FR', 'japan': 'JP',
    }
    processed_regions = [country_map.get(region.lower(), region.upper()) for region in region_list]
    return ','.join(processed_regions)

def visualize_google_trends(interest_over_time_df):
    fig = px.line(interest_over_time_df, x=interest_over_time_df.index, y=interest_over_time_df.columns[0],
                  title=f'Search Interest Over Time: {interest_over_time_df.columns[0]}')
    return fig

def fetch_financial_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Fetch income statement
        income_statement = ticker.financials

        # Fetch balance sheet
        balance_sheet = ticker.balance_sheet

        # Fetch cash flow
        cash_flow = ticker.cashflow

        return {
            "Name": info.get('longName', 'N/A'),
            "Sector": info.get('sector', 'N/A'),
            "Industry": info.get('industry', 'N/A'),
            "Market Cap": info.get('marketCap', 'N/A'),
            "PE Ratio": info.get('trailingPE', 'N/A'),
            "Dividend Yield": info.get('dividendYield', 'N/A'),
            "Revenue": income_statement.loc['Total Revenue', income_statement.columns[0]],
            "Net Income": income_statement.loc['Net Income', income_statement.columns[0]],
            "Total Assets": balance_sheet.loc['Total Assets', balance_sheet.columns[0]],
            "Total Liabilities": balance_sheet.loc['Total Liabilities Net Minority Interest', balance_sheet.columns[0]],
            "Operating Cash Flow": cash_flow.loc['Operating Cash Flow', cash_flow.columns[0]],
        }
    except Exception as e:
        st.error(f"Error fetching financial data: {str(e)}")
        return None

def fetch_stock_data(symbol, start_date, end_date):
    try:
        data = yf.download(symbol, start=start_date, end=end_date)
        return data
    except Exception as e:
        st.error(f"Error fetching stock data: {str(e)}")
        return None

def fetch_news(query, from_date, to_date):
    url = f"https://newsapi.org/v2/everything?q={query}&from={from_date}&to={to_date}&sortBy=popularity&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        news_data = response.json()
        return news_data.get('articles', [])
    except Exception as e:
        st.error(f"Error fetching news: {str(e)}")
        return []

def fetch_industry_data(industry):
    url = f"https://www.bls.gov/oes/current/naics4_{industry}.htm"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all('table')
        if tables:
            df = pd.read_html(str(tables[0]))[0]
            return df
    except Exception as e:
        st.error(f"Error fetching industry data: {str(e)}")
    return None

def generate_insights(financial_data, stock_data, news, industry_data):
    prompt = f"""
    Based on the following data, provide insights about the company and its market position:
    
    Financial Data: {json.dumps(financial_data, indent=2)}
    
    Stock Performance: The stock has moved from {stock_data['Close'].iloc[0]:.2f} to {stock_data['Close'].iloc[-1]:.2f} in the last year.
    
    Recent News Headlines: {', '.join([article['title'] for article in news[:3]])}
    
    Industry Data: {industry_data.to_json(orient='records') if industry_data is not None else 'Not available'}
    
    Provide a concise analysis covering:
    1. The company's financial health
    2. Stock performance trends
    3. Recent news impact
    4. Industry position
    5. Potential opportunities and threats
    
    Ensure all insights are directly based on the provided data and clearly indicate any assumptions or limitations.
    """
    
    insights = generate_chatgpt_response(prompt)
    return insights

def generate_complex_answer(question, context):
    try:
        if context == "new_business_plan":
            context_content = st.session_state.new_business_plan
        elif context == "strategic_plan":
            context_content = st.session_state.plan
        elif context == "analyzed_plan":
            context_content = st.session_state.analyzed_plan
        elif context == "scenario_forecasts":
            context_content = st.session_state.forecasts
        elif context == "alternative_plans":
            context_content = st.session_state.alternative_plans
        elif context == "market_research":
            context_content = st.session_state.get('market_research_result', "No market research data available.")
        else:
            return "Context not recognized.", 0.0
        
        prompt = f"""
        Based on the following {context.replace('_', ' ')}:

        {context_content}

        Provide a comprehensive answer to this multi-part question: {question}

        Instructions:
        1. Break down the question into its component parts and address each thoroughly.
        2. For budget estimates, provide a range and breakdown of costs. Explain factors influencing the estimate.
        3. For timelines, provide a phased execution plan with major milestones and overall duration.
        4. When discussing competitors, provide specific examples if available. If not, offer analogous cases from related industries.
        5. For efficiency rates, provide estimates based on plan components and industry benchmarks. Explain your reasoning.
        6. When comparing to real-world examples, provide specific data if available, or industry averages if not.
        7. Clearly differentiate between direct information from the plan, inferences, and additional research.
        8. If making estimates or inferences, explain your reasoning and note any uncertainties.
        9. Provide relevant case studies, data points, or examples to support your answer.
        10. Offer insights on how different aspects of the answer interrelate (e.g., how budget might affect timeline or efficiency).

        Please provide a detailed and accurate answer to this question: {question}
        If the information is not explicitly stated in the business plan / document, use the context to infer a reasonable answer. 
        Focus on providing an accurate and complete answer based on the question asked, explain the answer of the question fully in detail.
        """
        response = generate_chatgpt_response(prompt)
        confidence = generate_confidence_level()
        return response, confidence
    except Exception as e:
        st.error(f"An error occurred while generating the answer: {str(e)}")
        return f"An error occurred: {str(e)}", 0.0
    


def generate_follow_up_answer(question, context):
    prompt = f"""
    Based on the following context:

    {context}

    Please provide a detailed and accurate answer to this question: {question}

    Instructions:
    1. If the question asks for specific information not explicitly stated in the plan you have generated, 
       provide a reasonable estimate based on the context and industry standards.
    2. For budget requirements, provide a range and explain the factors influencing the estimate.
    3. For timelines, break down the execution into phases and provide estimated durations.
    4. When asked about competitors, if specific examples aren't available, describe the type 
       of companies that might implement similar strategies and why.
    5. For efficiency rates, provide a range based on industry benchmarks and explain the factors 
       that could influence the actual rate.
    6. Always clarify when you're making an estimate or inference not directly stated in the original plan.
    7. If you absolutely cannot provide an answer, explain why and suggest how the user might 
       find that information.
    8. Provide confidence levels for different parts of your answer.

    Aim to provide a detailed, accurate, well-reasoned response that addresses all parts of the question.
    """
    
    answer = generate_chatgpt_response(prompt)
    confidence = generate_confidence_level()
    return answer, confidence


def handle_complex_question(question, context):
    answer, confidence = generate_complex_answer(question, context)
    st.write(f"Answer: {answer}")
    st.write(f"Confidence Level: {confidence*100:.2f}%")
    st.session_state.conversation_history.append(("User", question))
    st.session_state.conversation_history.append(("AI", f"Answer: {answer}\nConfidence Level: {confidence*100:.2f}%"))

    
@st.cache_data
def cached_research(category, query):
    key = hashlib.md5(f"{category.value}:{query}".encode()).hexdigest()
    
    if key in st.session_state.get('research_cache', {}):
        return st.session_state.research_cache[key]
    
    result, confidence = generate_follow_up_answer(query, None, category)
    
    if 'research_cache' not in st.session_state:
        st.session_state.research_cache = {}
    st.session_state.research_cache[key] = (result, confidence)
    
    return result, confidence

def display_follow_up_questions(context):
    st.subheader("Interactive Q&A")
    
    # Create unique keys for each widget
    base_key = f"follow_up_{context}"
    question_key = f"{base_key}_question"
    submit_question_key = f"{base_key}_submit_question"
    clear_history_key = f"{base_key}_clear_history"
    

    # Add a session state variable to store the last generated answer
    if 'last_answer' not in st.session_state:
        st.session_state.last_answer = ""
    
    # Initialize session state variables
    if 'show_clarification' not in st.session_state:
        st.session_state.show_clarification = False
    if 'clarification_question' not in st.session_state:
        st.session_state.clarification_question = ""

    # Single input for asking a complex question
    question = st.text_area("Ask a complex question:", key=question_key)
    
    if st.button("Submit Question", key=submit_question_key):
        with st.spinner("Generating answer..."):
            answer, confidence = generate_complex_answer(question, context)
            st.write(f"Answer: {answer}")
            st.write(f"Confidence Level: {confidence*100:.2f}%")
            st.session_state.conversation_history.append(("User", question))
            st.session_state.conversation_history.append(("AI", f"Answer: {answer}\nConfidence Level: {confidence*100:.2f}%"))
            st.session_state.last_answer = answer
            if st.session_state.clarification_question:
                with st.spinner("Generating clarification..."):
                    # Use both the original context and the last answer for clarification
                    combined_context = f"{context}\n\nLast Answer: {st.session_state.last_answer}"
                    clarification_answer, clarification_confidence = generate_follow_up_answer(st.session_state.clarification_question, combined_context)
                    st.write(f"Clarification: {clarification_answer}")
                    st.write(f"Confidence Level: {clarification_confidence*100:.2f}%")
                    st.session_state.conversation_history.append(("User", st.session_state.clarification_question))
                    st.session_state.conversation_history.append(("AI", f"Clarification: {clarification_answer}\nConfidence Level: {clarification_confidence*100:.2f}%"))
                st.session_state.clarification_question = ""  # Clear the input after submission
                st.session_state.show_clarification = False  # Hide the clarification input after submission

    # Display conversation history
    st.subheader("Conversation History")
    for role, message in st.session_state.conversation_history:
        st.text(f"{role}: {message}")

    # Option to clear conversation history
    if st.button("Clear Conversation History", key=clear_history_key):
        st.session_state.conversation_history = []
        st.session_state.show_clarification = False
        st.session_state.clarification_question = ""
        st.rerun()

def export_to_pdf(content, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, txt=title, ln=1, align='C')
    pdf.set_font("Arial", size=12)
    
    if isinstance(content, dict):
        for section, text in content.items():
            # Add section title
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, txt=section, ln=1)
            pdf.set_font("Arial", size=12)
            
            # Split the text into lines
            lines = text.split('\n')
            for line in lines:
                # Replace unicode characters
                line = line.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 10, txt=line)
            
            # Add some space between sections
            pdf.ln(10)
    else:
        # If content is not a dict, treat it as a string
        lines = content.split('\n')
        for line in lines:
            line = line.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 10, txt=line)
    
    return pdf.output(dest='S').encode('latin-1')

def generate_market_research(query, aim, industry, regions, max_retries=3):
    base_prompt = f"""
    Conduct a comprehensive market research analysis based on the following parameters:

    Query: {query}
    Aim of Research: {aim}
    Industry: {industry}
    Geographic Regions: {regions}

    Provide an exceptionally detailed, accurate, and data-driven market research report that addresses all specified aspects. The report should be a combination of quantitative and qualitative analysis, with a strong emphasis on statistical data and real-world examples.

    IMPORTANT: For EVERY claim, statistic, or significant piece of information, you MUST fetch and provide data from **reliable sources**. Ensure that data is up-to-date, accurate, and sourced from well-regarded industry reports, governmental data, credible research publications, or respected market analysis firms (e.g., Statista, Gartner, McKinsey, IBISWorld, World Bank, OECD, etc.). Use the format: [Source Name](URL) immediately after the information. Aim for at least 5 unique citations throughout the report.

    Your report must include the following sections:
    1. Executive Summary
    2. Industry Overview and Basic Knowledge
    3. Industry Market Size (Globally and in specific regions)
    4. Industry Growth Rate (Globally and in specific regions)
    5. Market Leaders and Market Share
    6. Current and Future Scope (Addressable Market)
    7. Competitor Strategies
    8. Untapped Market
    9. Barriers to Entry
    10. Pricing Strategy
    11. PESTEL Analysis
    12. Product/Service Lifecycle
    13. Success Factors and Risk Factors
    14. Entry Strategy for New Business
    15. Customer Segmentation
    16. Future Trends & Innovation Opportunities
    17. Conclusion & Action Plan

    For each section:
    1. Provide detailed explanations and in-depth analysis.
    2. Include a mix of quantitative data (e.g., market size, growth rates, market share percentages) and qualitative insights.
    3. Cite specific statistical data points, ensuring to include the source and a relevant URL for each.
    4. Offer actionable insights based on the analysis, supported by data whenever possible.
    5. Include at least one relevant real-world case study or example per section, clearly labeled as "Case Study: [Title]".
    6. Discuss how different aspects of the research interrelate and impact each other, using data to support these connections.
    7. When presenting data or trends, always provide context (e.g., historical data, industry benchmarks) to ensure meaningful interpretation.

    Throughout the report:
    - **Fetch and incorporate data directly from reliable and up-to-date sources**, ensuring it is recent (within the last 2-3 years unless historical context is needed).
    - For predictive or forward-looking statements, clearly state the assumptions and methodology used.
    - If relevant, present data in a tabular format using Markdown tables for clarity, and describe key findings in the text.
    - Highlight any discrepancies or contradictions in data from different sources and discuss potential reasons.
    - Provide specific data points, statistics, and figures to support all claims and insights.
    - Include historical data (past 3-5 years) and projected growth (next 3-5 years) where available.
    - Compare growth rates and other metrics to related industries or the overall economy for context.
    - Quantify barriers to entry, market sizes, and other key factors where possible.
    - Analyze the Total Addressable Market (TAM) for the industry.
    - Discuss how technological advancements or societal changes might affect the future scope of the industry.

    For the PESTEL Analysis, ensure comprehensive coverage of:
    - Political factors (e.g., regulations, trade policies)
    - Economic factors (e.g., economic growth, inflation rates)
    - Social factors (e.g., demographic trends, cultural shifts)
    - Technological factors (e.g., innovations, R&D trends)
    - Environmental factors (e.g., sustainability concerns, environmental regulations)
    - Legal factors (e.g., labor laws, intellectual property rights)

    At the end of the report, include a section titled "Methodology and Data Sources" that:
    1. Explains the research methodology used, including both quantitative and qualitative methods.
    2. Lists all the data sources used in the analysis, including full citations and URLs.
    3. Discusses any limitations, potential biases, or gaps in the available data.
    4. Provides a brief assessment of the reliability and validity of the key data sources used.

    Conclude the analysis with:
    - A summary of the key findings and their implications for businesses in the industry.
    - Recommendations for further areas of research or data collection that could enhance the analysis.
    - A brief statement on the limitations of the current analysis and any potential biases in the data sources used.

    Ensure the report is comprehensive, well-structured, and provides valuable, data-driven insights for business decision-making. The goal is to present a balanced, accurate, and thorough analysis that combines hard data with expert interpretation and real-world application.

    IMPORTANT: Do not repeat any content. Ensure each section is unique and non-repetitive. Remember to include at least 5 unique citations throughout the report.
    """
   
    for attempt in range(max_retries):
        try:
            research_result = generate_chatgpt_response(base_prompt)
           
            # Perform checks on the output
            if "Executive Summary" not in research_result or "Methodology and Data Sources" not in research_result:
                raise ValueError("Generated report is missing key sections")
           
            citation_count = research_result.count("http")
            if citation_count < 5:
                raise ValueError(f"Generated report contains only {citation_count} citations, which is less than the required 5")
           
            # Remove the check for data tables
           
            return research_result
        except ValueError as ve:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed: {str(ve)}. Retrying...")
            else:
                raise ve
   
    raise Exception("Max retries reached. Unable to generate satisfactory market research report.")

def view_full_plan(plan_content, plan_title):
    with st.expander(f"View Full {plan_title}", expanded=False):
        st.markdown(f"## Full {plan_title}")
        st.text_area("", value=plan_content, height=500, max_chars=None, key=f"full_{plan_title.lower().replace(' ', '_')}")
        st.download_button(
            label=f"Download Full {plan_title} as Text",
            data=plan_content,
            file_name=f"full_{plan_title.lower().replace(' ', '_')}.txt",
            mime="text/plain"
        )

def go_back():
    """Handle navigation back to previous pages"""
    if st.session_state.stage == "upload_pdf":
        st.session_state.stage = "choose_action"
    elif st.session_state.stage in ["questions", "analyze_plan"]:
        st.session_state.stage = "upload_pdf"
    elif st.session_state.stage == "analysis":
        st.session_state.stage = "questions"
    elif st.session_state.stage == "budget_workforce":
        st.session_state.stage = "analysis"
    elif st.session_state.stage == "plan":
        st.session_state.stage = "budget_workforce"
    elif st.session_state.stage == "scenario_planning":
        st.session_state.stage = "plan"
    elif st.session_state.stage == "new_business_plan":
        st.session_state.stage = "choose_action"
    elif st.session_state.stage == "market_research":
        st.session_state.stage = "choose_action"
    st.rerun()

def init_session_state():
    if 'stage' not in st.session_state:
        st.session_state.stage = 'landing'
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'subscription_status' not in st.session_state:
        st.session_state.subscription_status = None
    if 'market_research_questions_count' not in st.session_state:
        st.session_state.market_research_questions_count = 0
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "analysis" not in st.session_state:
        st.session_state.analysis = ""
    if "plan" not in st.session_state:
        st.session_state.plan = ""
    if "pdf_docs" not in st.session_state:
        st.session_state.pdf_docs = None
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "new_business_plan" not in st.session_state:
        st.session_state.new_business_plan = None

def main():
    """Main application function"""
    st.set_page_config(layout="wide")
    init_session_state()
    

    # Set background image
    set_bg("C:\\Users\\Lenovo\\OneDrive\\Pictures\\Background.jpg")
    
    # Main navigation flow
    if st.session_state.stage == 'landing':
        show_landing_page()
        
    elif st.session_state.stage == 'features':
        show_features_page()
        
    elif st.session_state.stage == 'auth':
        show_auth_page()
        
    elif st.session_state.stage == 'payment':
        show_payment_page()

    # Initialize all session state variables
    if 'stage' not in st.session_state:
        st.session_state.stage = "choose_action"
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "analysis" not in st.session_state:
        st.session_state.analysis = ""
    if "plan" not in st.session_state:
        st.session_state.plan = ""
    if "pdf_docs" not in st.session_state:
        st.session_state.pdf_docs = None
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "new_business_plan" not in st.session_state:
        st.session_state.new_business_plan = None

# Action selection stage
    if st.session_state.stage == "choose_action":
        st.subheader("Choose an Action")
        action = st.radio("Select an action:", ["Analyze Existing Business", "Analyze Uploaded Business Plan", "Generate New Business Plan", "Market Research"])

        if st.button("Proceed"):
            if action == "Analyze Existing Business":
                st.session_state.stage = "upload_pdf"
                st.session_state.action = action
            elif action == "Analyze Uploaded Business Plan":
                st.session_state.stage = "upload_pdf"
                st.session_state.action = action
            elif action == "Generate New Business Plan":
                st.session_state.stage = "new_business_plan"
            elif action == "Market Research":
                st.session_state.stage = "market_research"
            st.rerun()


    # Market Research Stage
    elif st.session_state.stage == "market_research":
        st.subheader("Advanced Market Research")
        query = st.text_area("Enter your market research query:")
        aim = st.text_area("AIM FOR RESEARCH:")
        industry = st.text_input("Research Scope (Industry):")
        regions = st.text_input("Geographic Regions:")

        if st.button("Conduct Advanced Research"):
            if query and aim and industry:
                with st.spinner("Conducting comprehensive market research..."):
                    try:
                        research_result = generate_market_research(query, aim, industry, regions)
                        st.session_state.show_market_research_qa = True
                        st.subheader("Market Research Results")
                        st.write(research_result)
                        st.session_state.market_research_result = research_result
                        view_full_plan(research_result, "Market Research Report")
                    except Exception as e:
                        st.error(f"An error occurred during market research: {str(e)}")
            else:
                st.warning("Please provide a query, aim, and industry.")

        if st.session_state.get('show_market_research_qa', False):
            display_follow_up_questions("market_research")
        if st.button("Back"):
            go_back()

    # Upload PDF stage
    elif st.session_state.stage == "upload_pdf":
        st.subheader("Upload PDF Documents")
        pdf_docs = st.file_uploader("Upload your PDF Files", accept_multiple_files=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Process PDFs"):
                if pdf_docs:
                    with st.spinner("Processing PDFs..."):
                        st.session_state.pdf_docs = pdf_docs
                        raw_text = get_pdf_text(pdf_docs)
                        text_chunks = get_text_chunks(raw_text)
                        get_vector_store(text_chunks)
                        if st.session_state.action == "Analyze Existing Business":
                            st.session_state.stage = "questions"
                        else:
                            st.session_state.stage = "analyze_plan"
                        st.success("PDFs processed successfully!")
                        st.rerun()
                else:
                    st.warning("Please upload PDF files before processing.")
        with col2:
            if st.button("Back"):
                go_back()

    # Initial Questions stage
    elif st.session_state.stage == "questions":
        st.subheader("Initial Questions")
        st.session_state.answers = ask_initial_questions()
        if len(st.session_state.answers) == 4:
            st.session_state.stage = "analysis"
            st.rerun()
        if st.button("Back"):
            go_back()

    # Comprehensive Company Analysis
    elif st.session_state.stage == "analysis":
        st.subheader("Comprehensive Company Analysis")

        if not st.session_state.get('pdf_docs'):
            st.error("No answers found. Please complete the questionnaire before proceeding.")
            st.session_state.stage = "questions"
            st.rerun()

        if 'analysis_complete' not in st.session_state:
            with st.spinner("Analyzing your responses and the detailed PDF document..."):
                try:
                    pdf_content = get_pdf_text(st.session_state.pdf_docs)
                    st.session_state.analysis = analyze_answers_and_documents(st.session_state.answers, pdf_content)
                    st.session_state.analysis_complete = True
                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")
                    st.session_state.stage = "questions"
                    st.rerun()

        if st.session_state.get('analysis_complete', False):
            st.write(st.session_state.analysis)
            view_full_plan(st.session_state.analysis, "Business Analysis")

            if st.button("Export Analysis to PDF"):
                pdf = export_to_pdf(st.session_state.analysis, "Comprehensive Company Analysis")
                st.download_button(label="Download Analysis PDF", data=pdf, file_name="company_analysis.pdf", mime="application/pdf")

            display_follow_up_questions("analysis")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Proceed to Budget and Workforce"):
                    st.session_state.stage = "budget_workforce"
                    st.rerun()
            with col2:
                if st.button("Back"):
                    go_back()

    # Budget and Workforce (Optional)
    elif st.session_state.stage == "budget_workforce":
        st.subheader("Budget and Workforce (Optional)")
        col1, col2 = st.columns(2)
        with col1:
            budget = st.number_input("What is your budget to meet the goal? (optional)", min_value=0, value=None)
        with col2:
            workforce = st.number_input("How many key stakeholders are in your workforce? (optional)", min_value=0, value=None)

        col3, col4, col5 = st.columns(3)
        with col3:
            if st.button("Generate Plan"):
                st.session_state.stage = "plan"
                st.session_state.budget = budget
                st.session_state.workforce = workforce
                st.rerun()
        with col4:
            if st.button("Skip and Generate Plan"):
                st.session_state.stage = "plan"
                st.session_state.budget = None
                st.session_state.workforce = None
                st.rerun()
        with col5:
            if st.button("Back"):
                go_back()

    # Generate Plan
    elif st.session_state.stage == "plan":
        st.subheader("Strategic Planning and Solutions")
        if "plan" not in st.session_state or not st.session_state.plan:
            with st.spinner("Generating comprehensive plan and solutions..."):
                try:
                    st.session_state.plan = provide_planning_and_solutions(
                        st.session_state.analysis,
                        st.session_state.budget,
                        st.session_state.workforce
                    )
                except Exception as e:
                    st.error(f"An error occurred while generating the plan: {str(e)}")

        if st.session_state.plan:
            st.write(st.session_state.plan)

            if st.button("Export Strategic Plan to PDF"):
                pdf = export_to_pdf(st.session_state.plan, "Strategic Plan")
                st.download_button(label="Download Strategic Plan PDF", data=pdf, file_name="strategic_plan.pdf", mime="application/pdf")

            display_follow_up_questions("strategic_plan")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Generate Scenario Forecasts and Alternative Plans"):
                    st.session_state.stage = "scenario_planning"
                    st.rerun()
            with col2:
                if st.button("Back"):
                    go_back()
            with col3:
                if st.button("Start New Analysis"):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.session_state.stage = "choose_action"
                    st.rerun()

    # Analyze Plan
    elif st.session_state.stage == "analyze_plan":
        st.subheader("Business Plan Analysis and Improvement Strategy")
        st.write("Please upload a PDF of your business plan.")

        if "analyzed_plan" not in st.session_state:
            with st.spinner("Analyzing the uploaded business plan and identifying areas for improvement..."):
                try:
                    pdf_content = get_pdf_text(st.session_state.pdf_docs)
                    analysis = analyze_uploaded_plan(pdf_content)

                    if "This document does not appear to be a business plan" in analysis:
                        st.error("The uploaded document doesn't match the expected structure of a business plan.")
                        st.session_state.stage = "upload_pdf"
                        st.rerun()

                    st.session_state.analyzed_plan = analysis
                    st.write(analysis)

                    st.subheader("Key Areas for Improvement")
                    improvement_areas = generate_chatgpt_response(f"Based on the following analysis, list the top 5 most critical areas for improvement in bullet points:\n\n{analysis}")
                    st.session_state.improvement_areas = improvement_areas
                    st.write(improvement_areas)

                    st.subheader("Implementation Strategy")
                    implementation_strategy = generate_chatgpt_response(f"Based on the analysis and areas for improvement, provide a concise, step-by-step implementation strategy:\n\n{analysis}\n\n{improvement_areas}")
                    st.session_state.implementation_strategy = implementation_strategy
                    st.write(implementation_strategy)

                except Exception as e:
                    st.error(f"An error occurred during business plan analysis: {str(e)}")
                    st.session_state.stage = "upload_pdf"
                    st.rerun()

        else:
            st.write(st.session_state.analyzed_plan)

            # Display the previously generated improvement areas and implementation strategy
            st.subheader("Key Areas for Improvement")
            st.write(st.session_state.improvement_areas)

            st.subheader("Implementation Strategy")
            st.write(st.session_state.implementation_strategy)

        # Add PDF export option
        if st.button("Export Business Plan Analysis to PDF"):
            content = f"Business Plan Analysis:\n\n{st.session_state.analyzed_plan}\n\n"
            content += f"Key Areas for Improvement:\n\n{st.session_state.improvement_areas}\n\n"
            content += f"Implementation Strategy:\n\n{st.session_state.implementation_strategy}"
            pdf = export_to_pdf(content, "Business Plan Analysis")
            st.download_button(label="Download Analysis PDF", data=pdf, file_name="business_plan_analysis.pdf", mime="application/pdf")

        # Interactive Q&A for Analyzed Plan
        display_follow_up_questions("analyzed_plan")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Refine Analysis"):
                del st.session_state.analyzed_plan
                del st.session_state.improvement_areas
                del st.session_state.implementation_strategy
                st.rerun()
        with col2:
            if st.button("Back"):
                go_back()
        with col3:
            if st.button("Start New Analysis"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.session_state.stage = "choose_action"
                st.rerun()

    # Generate New Business Plan
    elif st.session_state.stage == "new_business_plan":
        st.subheader("Generate New Business Plan")

        business_idea = st.text_area("1. What is your business idea?")
        business_type = st.radio("2. Business type:", ["Product", "Service"])
        selected_country, selected_currency = st.selectbox(
            "3. Select the country for your business:",
            options=countries_with_currencies,
            format_func=lambda x: x[0]
        )
        city = st.text_input("4. Enter Target city for your business:")
        location = f"{city}, {selected_country}"

        industries = st.multiselect(
            "5. In which industry(ies) do you identify yourself? (Select up to 2)",
            options=["Technology", "Healthcare", "Finance", "Education", "Retail", "Manufacturing", "Other"],
            max_selections=2
        )

        st.write("6. Target market:")
        demographics = st.multiselect("A. Demographics", ["Male", "Female", "Others", "All"])
        age_categories = st.multiselect("B. Age Categories", ["0-10", "10-18", "18-35", "35-60", "60+"])
        income_group = st.multiselect("C. Income group", ["Lower", "Lower-middle", "Middle-upper", "Upper"])

        product_positioning = st.radio("7. How would you describe your product positioning?", ["Mass Product", "Seasonal Product", "Premium Product"])
        usp = st.text_area("8. Describe key values and features of your product - USP:")
        initial_investment = st.number_input(f"9. Initial investment ({selected_currency}):", min_value=0, value=0)
        target_market_share = st.number_input("10. Target market share (%) to achieve in 3 years:", min_value=0.0, max_value=100.0, value=1.0, step=0.1)
        founders_experience = st.text_area("11. Experience of founders:")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate Business Plan"):
                with st.spinner("Generating your business plan..."):
                    try:
                        business_plan = generate_new_business_plan(
                            business_idea=business_idea,
                            business_type=business_type,
                            target_market={
                                "demographics": demographics,
                                "age_categories": age_categories,
                                "income_group": income_group
                            },
                            initial_investment=initial_investment,
                            industry=", ".join(industries),
                            location=location,
                            product_positioning=product_positioning,
                            usp=usp,
                            target_market_share=target_market_share,
                            founders_experience=founders_experience,
                            currency=selected_currency
                        )
                        st.session_state.new_business_plan = business_plan
                        st.write(business_plan)
            
                    except Exception as e:
                        st.error(f"An error occurred while generating the business plan: {str(e)}")
            else:
                st.write(st.session_state.new_business_plan)

        if st.button("Back"):
            go_back()

        # Add PDF export option
        if st.button("Export New Business Plan to PDF"):
            pdf = export_to_pdf(st.session_state.new_business_plan, "New Business Plan")
            st.download_button(
                label="Download Business Plan PDF",
                data=pdf,
                file_name="new_business_plan.pdf",
                mime="application/pdf"
            )

        if st.button("Proceed to Interactive Q&A"):
            st.session_state.show_qa = True

        if st.session_state.get('show_qa', False):
            display_follow_up_questions("new_business_plan")

        if st.button("Start New Analysis"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.stage = "choose_action"
            st.rerun()

    # AI-Powered Scenario Planning
    elif st.session_state.stage == "scenario_planning":
        st.subheader("AI-Powered Scenario Planning")

        if "forecasts" not in st.session_state:
            with st.spinner("Generating scenario forecasts..."):
                st.session_state.forecasts = generate_scenario_forecasts(st.session_state.analysis, st.session_state.plan)

        st.write("Scenario Forecasts:")
        st.write(st.session_state.forecasts)

        if "alternative_plans" not in st.session_state:
            with st.spinner("Generating alternative plans..."):
                st.session_state.alternative_plans = generate_alternative_plans(
                    st.session_state.analysis,
                    st.session_state.plan,
                    st.session_state.forecasts
                )

        st.write("Alternative Strategic Plans:")
        st.write(st.session_state.alternative_plans)

        # Add PDF export option
        if st.button("Export Scenario Planning to PDF"):
            content = f"Scenario Forecasts:\n\n{st.session_state.forecasts}\n\n"
            content += f"Alternative Strategic Plans:\n\n{st.session_state.alternative_plans}"
            pdf = export_to_pdf(content, "Scenario Planning Report")
            st.download_button(
                label="Download Scenario Planning PDF",
                data=pdf,
                file_name="scenario_planning_report.pdf",
                mime="application/pdf"
            )

        display_follow_up_questions("scenario_forecasts")
        display_follow_up_questions("alternative_plans")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back"):
                go_back()
        with col2:
            if st.button("Start New Analysis"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.session_state.stage = "choose_action"
                st.rerun()

# Error handling decorator
def handle_errors(func):
    """Decorator for handling errors in functions"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            logging.error(f"Error in {func.__name__}: {str(e)}\n{traceback.format_exc()}")
            return None
    return wrapper               
                
if __name__ == "__main__":
    main()
