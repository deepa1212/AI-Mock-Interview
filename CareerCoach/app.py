import streamlit as st
from datetime import datetime
from database import init_db, create_user, authenticate, save_interview
from question_bank import get_question_set
from resume_parser import extract_resume_text
from llm_pipeline import evaluate_answer, generate_next_question, chat_intro_response

st.set_page_config(page_title="CareerCoach", page_icon="🎯", layout="wide")
with open("assets/style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_db()

def init_state():
    defaults = {
        "page": "Home",
        "user": None,
        "role": "",
        "level": "",
        "resume_text": "",
        "intro_started": False,
        "intro_index": 0,
        "intro_answers": [],
        "intro_messages": [],
        "interview_started": False,
        "questions": [],
        "current_q": 0,
        "answers": [],
        "evaluations": [],
        "last_result": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

def reset_interview():
    st.session_state.intro_started = False
    st.session_state.intro_index = 0
    st.session_state.intro_answers = []
    st.session_state.intro_messages = []
    st.session_state.interview_started = False
    st.session_state.questions = []
    st.session_state.current_q = 0
    st.session_state.answers = []
    st.session_state.evaluations = []
    st.session_state.last_result = None

def login_screen():
    st.markdown('<div class="hero"><h1>🎯 CareerCoach</h1><p>AI-Powered Mock Interview Platform</p></div>', unsafe_allow_html=True)
    st.write("")
    tab1, tab2 = st.tabs(["Login", "Create Account"])

    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", type="primary", use_container_width=True):
            user = authenticate(username, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Invalid username or password.")

    with tab2:
        username = st.text_input("Create username", key="new_user")
        password = st.text_input("Create password", type="password", key="new_pass")
        if st.button("Create Account", type="primary", use_container_width=True):
            if not username or not password:
                st.warning("Enter username and password.")
            else:
                candidate = create_user(username, password)
                if candidate:
                    st.success(f"Account created. Your Candidate Number is {candidate}")
                else:
                    st.error("Username already exists.")

if not st.session_state.user:
    login_screen()
    st.stop()

with st.sidebar:
    st.markdown("## 🎯 CareerCoach")
    st.caption(f"Candidate: {st.session_state.user['candidate_number']}")
    nav = st.radio(
        "Navigation",
        ["Home", "Interview Prep", "Courses", "Career Assessment", "Settings", "About"]
    )
    st.session_state.page = nav
    if st.button("Logout"):
        st.session_state.user = None
        reset_interview()
        st.rerun()

def home():
    st.markdown('<div class="hero"><h1>CareerCoach</h1><p>Practice. Improve. Get Interview Ready.</p></div>', unsafe_allow_html=True)
    st.write("")
    c1, c2, c3 = st.columns(3)
    c1.metric("Technical Questions", "20")
    c2.metric("Time / Question", "90 sec")
    c3.metric("Pass Mark", "80%")
    st.info("Go to Interview Prep to configure your interview and start the candidate chat.")

def interview_prep():
    st.markdown('<div class="chat-title">💬 Interview Preparation</div>', unsafe_allow_html=True)

    if not st.session_state.interview_started and not st.session_state.intro_started:
        st.subheader("1. Interview Setup")
        role = st.selectbox("Select Role", ["AI/ML Engineer", "Cloud/AWS Engineer", "Data Engineer", "Python Developer", "DevOps Engineer"])
        level = st.selectbox("Select Level", ["Fresher", "Junior", "Mid-Level", "Senior"])
        resume = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])

        if resume:
            st.session_state.resume_text = extract_resume_text(resume)

        st.subheader("2. Before the Technical Interview")
        st.write("The chatbot will ask you four questions in chat. Reply to each question, and only after all four answers will the technical interview begin.")

        if st.button("Start Candidate Chat", type="primary", use_container_width=True):
            st.session_state.role = role
            st.session_state.level = level
            st.session_state.intro_started = True
            st.session_state.intro_index = 0
            st.session_state.intro_answers = []
            st.session_state.intro_messages = []
            st.rerun()
        return

    if st.session_state.intro_started and not st.session_state.interview_started:
        intro_questions = [
            "What is your good name?",
            "Tell me about yourself.",
            "Why are you interested in this role?",
            "Walk me through your resume."
        ]

        st.markdown("### 🤖 CareerCoach Interviewer")
        st.caption(f"Role: {st.session_state.role} • Level: {st.session_state.level}")

        # Render chat history
        for msg in st.session_state.intro_messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        idx = st.session_state.intro_index

        if idx < len(intro_questions):
            # Add the current interviewer question only once.
            current_question = intro_questions[idx]
            has_current_question = (
                st.session_state.intro_messages
                and st.session_state.intro_messages[-1]["role"] == "assistant"
                and st.session_state.intro_messages[-1]["content"] == current_question
            )

            if not has_current_question:
                st.session_state.intro_messages.append({
                    "role": "assistant",
                    "content": current_question
                })
                st.rerun()

            answer = st.chat_input(
                f"Answer Question {idx + 1} of {len(intro_questions)}..."
            )

            if answer and answer.strip():
                # Store candidate response.
                st.session_state.intro_messages.append({
                    "role": "user",
                    "content": answer.strip()
                })
                st.session_state.intro_answers.append(answer.strip())

                # Short acknowledgement.
                try:
                    acknowledgement = chat_intro_response(current_question, answer.strip())
                except Exception:
                    acknowledgement = "Thank you for your answer."

                st.session_state.intro_messages.append({
                    "role": "assistant",
                    "content": acknowledgement
                })

                # Move to the NEXT question.
                st.session_state.intro_index = idx + 1

                # If another question remains, immediately append it so it
                # is visible in the chat and the candidate can answer it.
                if st.session_state.intro_index < len(intro_questions):
                    st.session_state.intro_messages.append({
                        "role": "assistant",
                        "content": intro_questions[st.session_state.intro_index]
                    })

                st.rerun()

        else:
            st.success("Pre-interview chat completed.")
            st.write("Your technical interview is ready to begin.")
            if st.button("🚀 Start Technical Interview", type="primary", use_container_width=True):
                st.session_state.questions = get_question_set(20)
                st.session_state.current_q = 0
                st.session_state.answers = []
                st.session_state.evaluations = []
                st.session_state.interview_started = True
                st.session_state.intro_started = False
                st.rerun()
        return

    if st.session_state.interview_started:
        qidx = st.session_state.current_q
        questions = st.session_state.questions

        if qidx >= len(questions):
            show_result()
            return

        st.markdown(f"### Technical Interview — Question {qidx + 1} of {len(questions)}")
        st.caption(f"Role: {st.session_state.role} • Level: {st.session_state.level}")
        st.markdown(f'<div class="question-card"><b>{questions[qidx]}</b></div>', unsafe_allow_html=True)

        answer_key = f"technical_answer_{qidx}"
        answer = st.text_area("Your answer", key=answer_key, height=180, placeholder="Type your answer here...")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅ Previous", disabled=(qidx == 0), use_container_width=True):
                st.session_state.current_q -= 1
                st.rerun()
        with col2:
            label = "Submit Answer & Next ➜" if qidx < len(questions)-1 else "Submit Final Answer"
            if st.button(label, type="primary", use_container_width=True):
                if not answer.strip():
                    st.warning("Please enter your answer before submitting.")
                    return

                with st.spinner("Evaluating your answer..."):
                    try:
                        result = evaluate_answer(questions[qidx], answer, st.session_state.role, st.session_state.level)
                    except Exception as e:
                        st.error(f"Could not evaluate answer. Check your Hugging Face token/model configuration. Error: {e}")
                        return

                if len(st.session_state.answers) <= qidx:
                    st.session_state.answers.append(answer)
                    st.session_state.evaluations.append(result)
                else:
                    st.session_state.answers[qidx] = answer
                    st.session_state.evaluations[qidx] = result

                # Show result for this question before moving.
                st.session_state.current_q += 1
                st.rerun()

def show_result():
    scores = [x.get("score", 0) for x in st.session_state.evaluations]
    overall = round(sum(scores) / len(scores), 1) if scores else 0
    passed = overall >= 80
    status = "PASS" if passed else "FAIL"

    st.markdown("## 🏁 Interview Completed")
    st.markdown(
        f'<div class="{"result-pass" if passed else "result-fail"}">{status} — Overall Score: {overall}%</div>',
        unsafe_allow_html=True
    )

    a, b, c = st.columns(3)
    a.metric("Technical Accuracy", f"{round(sum(x.get('technical_accuracy',0) for x in st.session_state.evaluations)/len(st.session_state.evaluations),1) if st.session_state.evaluations else 0}%")
    b.metric("Clarity", f"{round(sum(x.get('clarity',0) for x in st.session_state.evaluations)/len(st.session_state.evaluations),1) if st.session_state.evaluations else 0}%")
    c.metric("Communication", f"{round(sum(x.get('communication',0) for x in st.session_state.evaluations)/len(st.session_state.evaluations),1) if st.session_state.evaluations else 0}%")

    st.subheader("Question-wise Feedback")
    for i, (q, ev) in enumerate(zip(st.session_state.questions, st.session_state.evaluations), start=1):
        icon = "✅" if ev.get("correct") else "❌"
        with st.expander(f"{icon} Question {i}: {q}"):
            st.write(f"**Score:** {ev.get('score', 0)}%")
            st.write(f"**Technical Accuracy:** {ev.get('technical_accuracy', 0)}%")
            st.write(f"**Clarity:** {ev.get('clarity', 0)}%")
            st.write(f"**Communication:** {ev.get('communication', 0)}%")
            st.write(f"**Feedback:** {ev.get('feedback', '')}")
            if ev.get("follow_up"):
                st.write(f"**Suggested follow-up:** {ev.get('follow_up')}")

    if not st.session_state.last_result:
        save_interview(
            st.session_state.user["candidate_number"],
            st.session_state.role,
            st.session_state.level,
            overall,
            status
        )
        st.session_state.last_result = {"score": overall, "status": status}

    if st.button("🔄 Start New Interview", type="primary"):
        reset_interview()
        st.rerun()

def courses():
    st.title("📚 Courses")
    st.write("Recommended learning areas: Python, AWS, Azure, AI/ML, Generative AI, SQL, DevOps.")

def assessment():
    st.title("🧭 Career Assessment")
    interest = st.selectbox("Which area interests you most?", ["AI/ML", "Cloud/AWS", "Data", "Python Development", "DevOps"])
    if st.button("Recommend Career"):
        mapping = {
            "AI/ML": "AI/ML Engineer",
            "Cloud/AWS": "Cloud/AWS Engineer",
            "Data": "Data Engineer",
            "Python Development": "Python Developer",
            "DevOps": "DevOps Engineer"
        }
        st.success(f"Recommended path: {mapping[interest]}")

def settings():
    st.title("⚙️ Settings")
    st.write(f"Candidate Number: **{st.session_state.user['candidate_number']}**")
    st.write(f"Username: **{st.session_state.user['username']}**")

def about():
    st.title("ℹ️ About CareerCoach")
    st.write("CareerCoach is an AI-powered mock interview application built with Streamlit, LangChain and Hugging Face.")

if st.session_state.page == "Home":
    home()
elif st.session_state.page == "Interview Prep":
    interview_prep()
elif st.session_state.page == "Courses":
    courses()
elif st.session_state.page == "Career Assessment":
    assessment()
elif st.session_state.page == "Settings":
    settings()
elif st.session_state.page == "About":
    about()
