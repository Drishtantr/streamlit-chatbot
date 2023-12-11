import streamlit as st
from rubric_streamlit import rubric
from pdf_chat_code import pdf_chat
from quiz_generator import quiz
from dotenv import load_dotenv


def main():
    st.header("Welcome to the LLM Exploration Tool!")
    st.write("This tool provides several functionalities to explore and understand the capabilities of Large Language Models (LLMs). Select a feature from the sidebar to get started.")

    st.subheader("PDF Chat")
    st.write("""
        The 'PDF Chat' feature allows users to upload PDF documents and interact with them using a chat interface. 
        It utilizes language models to understand and respond to queries based on the content of the uploaded PDFs.
    """)

    st.subheader("Rubric Generator")
    st.write("""
        The 'Rubric Generator' section provides a tool for generating grading rubrics. 
        This feature is especially useful for educators and trainers who need to create detailed and consistent assessment criteria.
    """)

    st.subheader("Quiz Generator")
    st.write("""
        The 'Quiz Generator' creates custom quizzes from provided texts. 
        This is an ideal tool for educators and learners, facilitating the creation of educational materials and self-assessment tools.
    """)


def render_sidebar():
    st.sidebar.title("Navigation")
    route = st.sidebar.radio("Go to", ["Home", "PDF_Chat", "Rubric", "Quiz"])
    return route


if __name__ == '__main__':
    load_dotenv()
    route = render_sidebar()

    if route == "PDF_Chat":
        pdf_chat()
    elif route == "Rubric":
        rubric()
    elif route == "Quiz":
        quiz()
    elif route == "Home":
        main()
