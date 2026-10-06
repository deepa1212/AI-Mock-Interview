import os
import json
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_BASE_URL = os.getenv("HF_BASE_URL", "https://router.huggingface.co/v1")
HF_MODEL = os.getenv("HF_MODEL", "google/gemma-4-E2B-it")

def build_chain(system_text, user_text):
    llm = ChatOpenAI(
        model=HF_MODEL,
        api_key=HF_TOKEN,
        base_url=HF_BASE_URL,
        temperature=0.2,
        max_tokens=1000
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_text),
        ("user", user_text)
    ])
    return prompt | llm | StrOutputParser()

def evaluate_answer(question, answer, role, level):
    system = """You are CareerCoach, a professional AI technical interviewer.
Evaluate a candidate's answer objectively. Return ONLY valid JSON.
Scoring:
- technical_accuracy: 0-100
- clarity: 0-100
- communication: 0-100
- score: weighted overall 0-100
correct=true when the answer is substantially correct.
feedback must be short and useful.
follow_up should be a relevant technical follow-up question."""
    user = f"""Role: {role}
Level: {level}
Question: {question}
Candidate answer: {answer}

Return:
{{
  "correct": true,
  "technical_accuracy": 0,
  "clarity": 0,
  "communication": 0,
  "score": 0,
  "feedback": "",
  "follow_up": ""
}}"""
    chain = build_chain(system, user)
    raw = chain.invoke({})
    raw = re.sub(r"```(?:json)?|```", "", raw).strip()
    try:
        return json.loads(raw)
    except Exception:
        return {
            "correct": False,
            "technical_accuracy": 0,
            "clarity": 0,
            "communication": 0,
            "score": 0,
            "feedback": "Unable to evaluate this answer.",
            "follow_up": ""
        }

def generate_next_question(role, level, previous_question, previous_answer, resume_text=""):
    system = """You are an adaptive technical interviewer.
Generate exactly ONE concise technical interview question based on the candidate's previous answer.
Do not include numbering, explanations, or JSON."""
    user = f"""Role: {role}
Level: {level}
Previous question: {previous_question}
Previous answer: {previous_answer}
Resume context: {resume_text[:4000]}
Generate the next technical question."""
    chain = build_chain(system, user)
    return chain.invoke({}).strip()

def chat_intro_response(question, answer):
    system = """You are CareerCoach conducting the candidate's pre-interview chat.
Respond briefly and professionally. Acknowledge the candidate's answer, then provide a natural transition.
Do not evaluate or score the candidate during this stage."""
    user = f"""Interviewer question: {question}
Candidate response: {answer}
Give a short interviewer-style acknowledgement."""
    chain = build_chain(system, user)
    return chain.invoke({}).strip()
