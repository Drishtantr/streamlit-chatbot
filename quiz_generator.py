import streamlit as st
import os
from dotenv import load_dotenv
import openai
from PyPDF2 import PdfReader

# Load the environment variable
load_dotenv('.env')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text() if page.extract_text() else ""
    return text


def generate_quiz(text):
    messages = [
        {"role": "system", "content": "You should create 10 questions from the text. The questions should be a mix of multiple choice or true and false."},
        {"role": "user", "content": text}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=2000,
        n=1,
        temperature=0
    )
    return response["choices"][0]["message"]["content"]


def quiz():
    st.title('Quiz Generator')
    pdf_docs = st.file_uploader(
        "Upload your PDFs here", accept_multiple_files=True)

    if pdf_docs:
        raw_text = get_pdf_text(pdf_docs)
        if st.button('Generate Quiz'):
            with st.spinner("Generating Quiz..."):
                try:
                    quiz_content = generate_quiz(raw_text)
                    st.text(quiz_content)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
