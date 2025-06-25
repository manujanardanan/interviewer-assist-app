
import streamlit as st
import openai
from resume_utils import extract_text_from_pdf, extract_text_from_docx, extract_relevant_experience
import pdfplumber
import docx
from io import StringIO

st.set_page_config(page_title="­ЪДа Interviewer Assist", layout="wide")
st.title("­ЪДа Interviewer Assistant")

client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_questions(jd, resume_exp):
    prompt = (
        "Based on the Job Description and Resume Experience below, generate two sets of interview questions.\n"
        "Set 1: To verify if the candidate truly did what is written in the resume.\n"
        "Set 2: To assess if the candidate has the knowledge to perform the job.\n"
        "For each question, add a short bullet on what the interviewer should listen for in the answer.\n"
        "Return in Markdown format.\n\n"
        f"Job Description:\n{jd}\n\nResume Experience:\n{resume_exp}"
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content

st.subheader("Step 1: Job Description")
jd_file = st.file_uploader("Upload JD (TXT, PDF, DOCX)", type=["txt","pdf","docx"])
if jd_file:
    if jd_file.name.endswith(".pdf"):
        with pdfplumber.open(jd_file) as pdf:
            jd_text = "\n".join([p.extract_text() or "" for p in pdf.pages])
    elif jd_file.name.endswith(".docx"):
        jd_text = "\n".join([p.text for p in docx.Document(jd_file).paragraphs])
    else:
        jd_text = StringIO(jd_file.getvalue().decode()).read()
else:
    jd_text = st.text_area("Or paste JD here", height=200)

st.subheader("Step 2: Candidate Resume")
resume_file = st.file_uploader("Upload Resume (PDF, DOCX)", type=["pdf","docx"])
if resume_file:
    if resume_file.name.endswith(".pdf"):
        raw = extract_text_from_pdf(resume_file)
    else:
        raw = extract_text_from_docx(resume_file)
    resume_exp = extract_relevant_experience(raw)
else:
    resume_exp = st.text_area("Or paste resume text here", height=200)

if st.button("Generate Interview Questions"):
    if jd_text and resume_exp:
        with st.spinner("Generating..."):
            q = generate_questions(jd_text, resume_exp)
        st.markdown(q)
    else:
        st.warning("Please provide both JD and Resume content.")
