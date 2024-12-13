import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import re

# Load environment variables
load_dotenv()  # Load all environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get a response from Gemini
def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content(input)
    return response.text

# Function to extract text from the uploaded PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Function to calculate a more accurate Resume Preparation Score
def calculate_resume_score(resume_text):
    score = 0
    word_count = len(resume_text.split())

    # Simple criteria for evaluating resume content:
    if 'experience' in resume_text.lower():
        score += 25
    if 'education' in resume_text.lower():
        score += 20
    if 'skills' in resume_text.lower():
        score += 20
    
    # Evaluate length of resume (300+ words)
    if word_count > 300:
        score += 10
    
    # Check for formatting markers (e.g., bullet points, dates, job titles)
    if len(re.findall(r'\•', resume_text)) > 3:  # Bullet points used for listing skills or experiences
        score += 10
    if len(re.findall(r'\d{4}', resume_text)) > 1:  # Detect dates (e.g., year of experience)
        score += 10

    # Normalize score to be between 0 and 100
    return min(score, 100)

# Chatbot Prompt Template
chatbot_prompt = """
You are a highly experienced Application Tracking System (ATS) with a deep understanding of the tech field, software engineering, data science, and big data engineering. You are reviewing the following resume and assisting with various queries:

Resume: {text}

User's Query: {query}

Please provide a standalone answer specific to this query.
"""

# Streamlit UI
st.title("Smart ATS Chatbot")
st.text("Ask questions about your resume!")

# File upload for the resume PDF
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload a PDF of your resume.")

# Store chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if uploaded_file is not None:
    text = input_pdf_text(uploaded_file)  # Extract text from the uploaded resume
    st.session_state.resume_text = text  # Save resume text for future queries

    # Display Resume Preparation Score
    resume_score = calculate_resume_score(text)
    st.subheader("Resume Preparation Score")
    st.write(f"Your Resume Preparation Score is: **{resume_score}%**")

    # Display instructions and chat history
    st.subheader("Chat with the ATS")
    user_query = st.text_input("Ask your question about your resume:")

    if user_query:
        # Prepare the prompt with user query and resume text
        formatted_prompt = chatbot_prompt.format(text=text, query=user_query)
        
        # Get response from the AI model
        response = get_gemini_response(formatted_prompt)

        # Add AI response to chat history for display purposes only (no context retention)
        st.session_state.chat_history.append({"role": "ats", "query": user_query, "response": response})

        # Display the current query and response
        st.write(f"**You:** {user_query}")
        st.write(f"**ATS:** {response}")

else:
    st.warning("Please upload a valid PDF file.")