from pathlib import Path
from docx import Document
import re

DOCX_PATH = Path("data/Technical_Interview_Question_Bank.docx")

def load_questions():
    if not DOCX_PATH.exists():
        return []
    doc = Document(DOCX_PATH)
    questions = []
    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue
        # Accept numbered questions from the uploaded question bank.
        if re.match(r"^\s*(?:\d+[\.\)]|Q\d+)", text, re.I):
            clean = re.sub(r"^\s*(?:\d+[\.\)]|Q\d+[\.\):\-]?)\s*", "", text).strip()
            if clean:
                questions.append(clean)
    return questions

def get_question_set(count=20):
    qs = load_questions()
    if not qs:
        return [
            "What is machine learning?",
            "Explain supervised and unsupervised learning.",
            "What is overfitting and how can you reduce it?",
            "What is a neural network?",
            "What is the difference between AI and machine learning?",
        ] * 4
    return [qs[i % len(qs)] for i in range(count)]
