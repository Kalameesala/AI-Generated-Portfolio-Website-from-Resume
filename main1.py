import streamlit as st
import os
import zipfile
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from PyPDF2 import PdfReader
import docx

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("gemini")

st.set_page_config(page_title="AI Resume to Portfolio Generator",page_icon="📄")

st.title("AI Resume → Portfolio Website Generator")

st.write("""Upload your resume (PDF or DOCX).""")

uploaded_file = st.file_uploader("Drag & Drop your Resume",type=["pdf", "docx"])

def extract_text(file):
    if file.type == "application/pdf":
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])

    return ""

if uploaded_file and st.button("Generate Portfolio Website"):

    resume_text = extract_text(uploaded_file)

    system_prompt = """
    You are an AI resume analyzer and frontend expert.

    Extract the following from the resume:
    - Name
    - Skills
    - Experience
    - Projects
    - Achievements
    - Education
    - Preferred modern design style

    Then generate a professional portfolio website.

    Output strictly in this format:

    --html--
    [HTML CODE]
    --html--

    --css--
    [CSS CODE]
    --css--

    --js--
    [JS CODE]
    --js--
    """

    messages = [
        ("system", system_prompt),
        ("user", resume_text)
    ]

    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
    response = model.invoke(messages)

    html_code = response.content.split("--html--")[1]
    css_code = response.content.split("--css--")[1]
    js_code = response.content.split("--js--")[1]

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_code)

    with open("style.css", "w", encoding="utf-8") as f:
        f.write(css_code)

    with open("script.js", "w", encoding="utf-8") as f:
        f.write(js_code)

    st.success("Portfolio Website Generated!")

    with zipfile.ZipFile("portfolio_website.zip", "w") as zipf:
        zipf.write("index.html")
        zipf.write("style.css")
        zipf.write("script.js")

    st.download_button(
        "Download Website ZIP",
        data=open("portfolio_website.zip", "rb"),
        file_name="portfolio_website.zip"
    )
