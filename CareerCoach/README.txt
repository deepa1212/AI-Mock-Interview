CAREERCOACH - CHAT-BASED AI MOCK INTERVIEW

1. Extract this ZIP.
2. Open the CareerCoach folder in VS Code.
3. Open .env and replace:
   HF_TOKEN=hf_your_actual_huggingface_token_here
   with your real Hugging Face token.
4. Open VS Code Terminal.
5. Run:
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
6. Run:
   streamlit run app.py
7. Open:
   http://localhost:8501

NEW INTERVIEW FLOW:
1. Candidate logs in.
2. Candidate selects Role and Level.
3. Candidate uploads Resume.
4. Candidate clicks "Start Candidate Chat".
5. The chatbot displays all four pre-interview questions one after another in the chat.
5. CareerCoach asks in chat:
   - What is your good name?
   - Tell me about yourself.
   - Why are you interested in this role?
   - Walk me through your resume.
6. Candidate replies to each question using the chat input.
7. CareerCoach acknowledges each response.
8. After all 4 responses, the "Start Technical Interview" button appears.
9. Technical interview starts with 20 questions.
10. Candidate answers each technical question.
11. Each answer is evaluated for technical accuracy, clarity and communication.
12. Final score is calculated.
13. 80% or above = PASS; below 80% = FAIL.

MODEL:
HF_MODEL uses google/gemma-4-E2B-it for the Hugging Face chat endpoint.
HF_ASSISTANT_MODEL records google/gemma-4-E2B-it-assistant as requested.

QUESTION BANK:
The uploaded Technical_Interview_Question_Bank.docx is included in data/ and is used to load numbered technical questions.

SUPPORTED RESUME TYPES:
PDF, DOCX, TXT

IMPORTANT:
- Never share your .env file or Hugging Face token.
- This is a local prototype, not production-grade authentication.
