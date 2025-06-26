import streamlit as st
import openai
from resume_utils import extract_text_from_pdf, extract_text_from_docx, extract_relevant_experience
import pdfplumber, docx
from io import StringIO

st.set_page_config(page_title="Interviewer Assistant", layout="wide")
st.title("🧠 Interviewer Assistant")

client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_questions(jd, resume_exp):
    prompt = (
        "You are an expert interviewer assistant.\n"
        "Generate exactly 10 interview questions based on the Job Description and Resume Experience below:\n"
        "- 4 questions to verify the truthfulness of the resume (Truth‑Check)\n"
        "- 4 questions to assess fit to the JD (Fit‑Check)\n"
        "- 2 scenario-based questions derived from the JD only (Scenario‑Based)\n"
        "Each question should be followed by a short bullet point that starts with 'Listen for:' — this tells the interviewer what kind of answer or evidence is expected.\n\n"
        "Return the response in Markdown with three sections:\n"
        "### Truth‑Check Questions\n"
        "* Q1 …\n  - Listen for: …\n"
        "### Fit‑Check Questions\n"
        "* Q2 …\n  - Listen for: …\n"
        "### Scenario‑Based Questions\n"
        "* Q9 …\n  - Listen for: …\n\n"
        f"Job Description:\n{jd}\n\nResume Experience:\n{resume_exp}"
    )
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return resp.choices[0].message.content

st.subheader("1️⃣ Job Description")
jd_file = st.file_uploader("Upload JD (TXT, PDF, DOCX)", type=["txt", "pdf", "docx"])
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

st.subheader("2️⃣ Candidate Resume")
res_file = st.file_uploader("Upload Resume (PDF, DOCX)", type=["pdf", "docx"])
if res_file:
    if res_file.name.endswith(".pdf"):
        raw = extract_text_from_pdf(res_file)
    else:
        raw = extract_text_from_docx(res_file)
    resume_exp = extract_relevant_experience(raw)
else:
    resume_exp = st.text_area("Or paste resume text here", height=200)

if st.button("Generate Interview Questions"):
    if jd_text and resume_exp:
        with st.spinner("Generating questions..."):
            result_md = generate_questions(jd_text, resume_exp)
        st.markdown(result_md)
    else:
        st.warning("Please provide both JD and Resume information.")
