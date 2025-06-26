
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
        "Generate exactly 8 interview questions based on the Job Description and Resume Experience below.\n"
        "- 4 questions to verify the truth of the candidate's resume claims.\n"
        "- 4 questions to assess whether the candidate has the knowledge and skills required by the JD.\n"
        "For each question, add a short bullet labelled 'Listen for:' that tells the interviewer what cues to listen for.\n"
        "Return output in Markdown with two sections: 'Truth‑Check Questions' and 'Fit‑Check Questions'.\n\n"
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
