import streamlit as st
import re
import pdfplumber
import os
import numpy as np
from datetime import date
from ai21 import AI21Client
from ai21.errors import UnprocessableEntity
from auth import register_user, login_user
from community import load_messages, post_message, delete_message, update_message, show_community
from export_pdf import generate_pdf, create_download_link
from dotenv import load_dotenv
# Suppress TensorFlow warnings

logo_path = 'logo.png'
# Load environment variables from .env file
# Directly assign the API key
api_key = "VkFkTvy0NxSmPYKJ9wNOWCqfAGeLqd9H"

# Check if the API key was assigned
if not api_key:
    raise ValueError("API key is missing")

# Initialize the AI21 client with the API key
client = AI21Client(api_key=api_key)


# Constants
max_chars = 200000
label = 'multi_doc' + str(date.today())
DOC_QA = "Ask a question about the uploaded documents:"

# Function to write text to a file
def write_to_library(segmented_text, file_name):
    folder_name = "file"
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    path = f"./{folder_name}/{file_name}.txt"
    with open(path, "w") as f:
        f.write(segmented_text)
    return path

# Function to upload file to AI21
def upload_file(file_path):
    endpoint = "https://api.ai21.com/studio/v1/library/files"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "file_path": file_path,
        "labels": label
    }

    try:
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        if response.status_code == 200:
            st.success("File uploaded successfully.")
        else:
            st.error(f"Unexpected status code: {response.status_code}")
            st.error(response.json())  # Print the full response for debugging
    except requests.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        st.error(f"Other error occurred: {err}")
# Function to parse uploaded files
def parse_file(user_file):
    file_type = user_file.type
    with st.spinner("File is being processed..."):
        if file_type == "text/plain":
            all_text = str(user_file.read(), "utf-8", errors='ignore')
        else:
            with pdfplumber.open(user_file) as pdf:
                all_text = [p.extract_text() for p in pdf.pages][0]
    file_path = write_to_library(all_text, user_file.name)
    return file_path

# Function to upload file to AI21
def upload_file(file_path):
    try:
        file_id = client.library.files.create(file_path=file_path, labels=label)
        st.session_state['files_ids'] = file_id
        st.session_state['file_uploaded'] = True
    except UnprocessableEntity:
        file_id = None
    return file_id

# Streamlit page configuration
st.set_page_config(page_title="Document Multiverse", layout="centered", page_icon=logo_path)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'history' not in st.session_state:
    st.session_state.history = []
if 'page' not in st.session_state:
    st.session_state.page = "Login"
if 'files_ids' not in st.session_state:
    st.session_state.files_ids = []

def show_login():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        success, msg = login_user(username, password)
        if success:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.page = "App"
            st.success(msg)
        else:
            st.error(msg)

def show_register():
    st.subheader("Register")
    username = st.text_input("Username", key="register_username")
    password = st.text_input("Password", type="password", key="register_password")
    if st.button("Register"):
        success, msg = register_user(username, password)
        if success:
            st.success(msg)
        else:
            st.error(msg)

def show_pdf_chat(): 
    paimage='sidebar.png'
    st.image(paimage, width=200)
    
    st.subheader("Universe Of Document Q&A")
    st.markdown("**Upload documents**")
    uploaded_files = st.file_uploader("Choose .pdf/.txt file(s)", accept_multiple_files=True, type=["pdf", "txt"], key="a")

    file_id_list = []
    file_path_list = []
    for uploaded_file in uploaded_files:
        file_path = parse_file(uploaded_file)
        file_id = upload_file(file_path)
        file_id_list.append(file_id)
        file_path_list.append(file_path)

    if st.button("Remove file"):
        for file in file_path_list:
            try:
                os.remove(file)
            except Exception as e:
                st.error(f"Error removing file: {e}")
        try:
            client.library.files.delete(st.session_state['files_ids'])
        except UnprocessableEntity:
            st.error("Error removing files from AI21")
        st.write("Files removed successfully")

    st.markdown("**Ask a question about the uploaded document, and here is the answer:**")
    question = st.chat_input(DOC_QA)
               
    if question:
        response = client.library.answer.create(question=question, label=label)
        if response.answer is None:
            st.write("The answer is not in the documents")
        else:
            st.write(response.answer)

def show_pdf_export():
    st.title("PDF Export Example")
    report_text = st.text_area("Enter Report Text", height=200)
    line_spacing = st.slider("Line Spacing", min_value=0.1, max_value=2.0, step=0.1, value=1.5)
    paragraph_spacing = st.slider("Paragraph Spacing", min_value=1, max_value=8, step=1, value=4)
    lines_per_paragraph = st.slider("Lines per Paragraph", min_value=1, max_value=10, step=1, value=5)
    export_as_pdf = st.button("Export Report")

    if export_as_pdf and report_text.strip():
        try:
            pdf_content = generate_pdf(report_text, line_spacing, paragraph_spacing, lines_per_paragraph)
            html_pdf = create_download_link(pdf_content, "report", file_format='pdf')
            html_txt = create_download_link(report_text.encode("utf-8"), "report", file_format='txt')
            st.markdown(html_pdf, unsafe_allow_html=True)
            st.markdown(html_txt, unsafe_allow_html=True)
            st.success("PDF and Text files successfully generated and ready for download!")
        except Exception as e:
            st.error(f"Error generating files: {e}")

def main_app():
    st.sidebar.title("Apps")
    page = st.sidebar.radio("Go to", ["Document Chat", "Student Community", "PDF Export"])
    if page == "Document Chat":
        show_pdf_chat()
    elif page == "Student Community":
        show_community()
    elif page == "PDF Export":
        show_pdf_export()
    
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.history = []
        st.session_state.page = "Login"

# Main app flow
if st.session_state.page == "App" and st.session_state.authenticated:
    main_app()
else:
    st.sidebar.image(logo_path, width=150)
    st.sidebar.title("Welcome To Multiverse")
    choice = st.sidebar.radio("Go to", ["Login", "Register"])
    if choice == "Login":
        show_login()
    elif choice == "Register":
        show_register()
