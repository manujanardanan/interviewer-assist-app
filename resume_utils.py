
import pdfplumber, docx, re

def extract_text_from_pdf(f):
    try:
        with pdfplumber.open(f) as pdf:
            return "\n".join([p.extract_text() or "" for p in pdf.pages])
    except:
        return ""

def extract_text_from_docx(f):
    try:
        d = docx.Document(f)
        return "\n".join([p.text for p in d.paragraphs])
    except:
        return ""

def extract_relevant_experience(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    start_sec = [
        "experience", "work history", "projects",
        "employment", "roles", "professional experience"
    ]
    end_sec = [
        "education", "certifications", "skills",
        "summary", "objective", "profile"
    ]
    start_re = re.compile(r"^\s*(" + "|".join(start_sec) + ")\s*$", re.I)
    end_re = re.compile(r"^\s*(" + "|".join(end_sec) + ")\s*$", re.I)

    capturing = False
    buf = []
    for l in lines:
        if start_re.match(l):
            capturing = True
            buf = []
            continue
        if capturing and end_re.match(l):
            break
        if capturing:
            buf.append(l)
    return "\n".join(buf) if buf else text
