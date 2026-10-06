from pathlib import Path
from docx import Document
from pypdf import PdfReader

def extract_resume_text(uploaded_file):
    if uploaded_file is None:
        return ""

    name = uploaded_file.name.lower()
    data = uploaded_file.getvalue()

    if name.endswith(".pdf"):
        import io
        reader = PdfReader(io.BytesIO(data))
        return "\n".join((p.extract_text() or "") for p in reader.pages)[:15000]

    if name.endswith(".docx"):
        import io
        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)[:15000]

    if name.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")[:15000]

    return ""
