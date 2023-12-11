import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
from dotenv import load_dotenv
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# 1526729, 1526730, 1526731, 1526732, 1499867


def rubric():
    load_dotenv('.env')

    st.header("Upload CSV file")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        st.write("File trimmed to only include questions")

        # Read the CSV file into a DataFrame
        df = pd.read_csv(uploaded_file)
        pattern = r'^\d+: .+'
        selected_columns = df.columns[df.columns.str.contains(pattern)]
        filtered_df = df[selected_columns]
        st.write(filtered_df)

        user_input = st.text_area(
            "Enter question IDs that require LLM (comma-separated)", "")

        if 'filtered_df' not in st.session_state:
            st.session_state.filtered_df = None
        if 'questions' not in st.session_state:
            st.session_state.questions = []

        if user_input:
            question_ids = [int(q.strip()) for q in user_input.split(',')]

        if st.button("Filter DataFrame"):
            selected_columns = [col for col in df.columns if any(
                col.startswith(str(num)) for num in question_ids)]
            st.session_state.filtered_df = df[selected_columns]
            st.session_state.questions = st.session_state.filtered_df.columns.tolist()

        if st.session_state.filtered_df is not None:
            st.write("Filtered DataFrame:")
            st.write(st.session_state.questions)

            st.title("Answer the Questions")
            result = gather_answers_and_grades(st.session_state.questions)

            if result:
                st.title("Rubrics")
                for question, answer, grade in result:
                    rubric = generate_rubric(question, answer, grade)
                    st.write(question)
                    st.write(rubric)

                if 'grading_results' not in st.session_state:
                    st.session_state.grading_results = []

                if st.button("Grade all answers using this rubric"):
                    for question, answer, grade in result:
                        user_answer = st.text_input(
                            f"Answer for {question}:", key=f"ans_{question}")
                        grading_response = get_answer(
                            question, user_answer, rubric)
                        st.session_state.grading_results.append(
                            grading_response)

                # Display grading results after they have been computed
                for grading_response in st.session_state.grading_results:
                    st.write(grading_response)


def gather_answers_and_grades(questions):
    data = []
    submission_flag = False

    for question in questions:
        st.subheader(question)
        answer = st.text_input(
            f"Enter your answer for {question}:", key=question)
        grade = st.slider(
            f"Grade (0-10) for {question}:", 0, 15, 5, key=f"grade_{question}")
        data.append([question, answer, grade])

    if st.button('Submit'):
        submission_flag = True

    if submission_flag:
        return data

    return None


def generate_rubric(question, answer, grade):
    messages = [
        {"role": "system",
         "content": """
    You should give a rubric to the question that I have. I also have an exact answer and the total possible points for the question.
    You should analyze the question and the output, and create a grading rubric. An example is:
    Grading Criteria:
    Total possible points: 3
    1. Correct Tune Identification (1 point):
       - Full Point (1): The student correctly identifies GEDG as the tune that will be returned by breadth-first search, providing a clear and accurate explanation of why.
       - Half Point (0.5): The student identifies the tune but lacks clarity in their explanation.
       - No Point (0): The student does not correctly identify the tune.
    2. Explanation of Breadth-First Search (1 point):
       - Full Point (1): The student provides a clear and accurate explanation of how breadth-first search works, emphasizing the horizontal traversal of the search tree and the principle of searching deeper layers after shallower layers.
       - Half Point (0.5): The student provides a partially accurate explanation or lacks clarity in describing the breadth-first search process.
       - No Point (0): The student's explanation is incorrect or unrelated to breadth-first search.
    3. Reasoning for Order of Return (1 point):
       - Full Point (1): The student gives a clear and accurate reason for why GEDG is returned first, linking it to the principle of breadth-first search and the desire to find the shortest sequence.
       - Half Point (0.5): The student provides a partially accurate reason or lacks clarity in their reasoning.
       - No Point (0): The student's reasoning is incorrect or unrelated to the search order.
    
    """},
        {"role": "user",
         "content": f"Question: {question} Answer: {answer} Grade: {grade}"}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=1800,
        n=1,
        temperature=0)

    return response["choices"][0]["message"]["content"]


def get_answer(question, answer, rubric):
    prompt1 = "Consider this question and answer: "
    prompt2 = "Grade this answer according to the following criteria:"
    Grader_Prompt = prompt1 + question + '\n' + answer + "\n" + prompt2 + rubric

    messages = [
        {"role": "system",
         "content": """When you are asked to grade an answer, you should take in the estimates and give result as: {Total: [grade]}. Also give a very brief description to the student (referring them as 'you') if they fail to obtain full marks."""},
        {"role": "user",
         "content": Grader_Prompt}
    ]

    # go with something more lightweight, -> PureCompletion
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=1800,
        n=1,
        temperature=0)

    return response["choices"][0]["message"]["content"]
