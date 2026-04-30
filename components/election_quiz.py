"""
CivicPulse — Election Quiz Component
=====================================
Gamified "How much do you know about Indian elections?" awareness quiz.
"""

from __future__ import annotations
import streamlit as st
import random

QUIZ_QUESTIONS = [
    {
        "q": "What is the minimum age to vote in Indian elections?",
        "options": ["16 years", "18 years", "21 years", "25 years"],
        "answer": "18 years",
        "explanation": "The 61st Constitutional Amendment (1988) reduced the voting age from 21 to 18 years.",
        "category": "Constitution",
    },
    {
        "q": "What does 'NOTA' stand for on the EVM?",
        "options": [
            "No Other Than Abstain",
            "None Of The Above",
            "Not Officially Tallied Again",
            "Neutral Option To Abstain",
        ],
        "answer": "None Of The Above",
        "explanation": "NOTA was introduced in 2013 following a Supreme Court order, allowing voters to reject all candidates.",
        "category": "Voting Process",
    },
    {
        "q": "What is the full form of EPIC?",
        "options": [
            "Electoral Photo Identity Card",
            "Election Public Identity Certificate",
            "Elector's Personal Identification Card",
            "Electoral Participation Identity Code",
        ],
        "answer": "Electoral Photo Identity Card",
        "explanation": "EPIC is the Voter ID card issued by the Election Commission of India (ECI).",
        "category": "Documents",
    },
    {
        "q": "Which article of the Indian Constitution establishes the Election Commission?",
        "options": ["Article 324", "Article 356", "Article 370", "Article 44"],
        "answer": "Article 324",
        "explanation": "Article 324 vests the superintendence, direction, and control of elections in the Election Commission.",
        "category": "Constitution",
    },
    {
        "q": "What is the maximum number of seats in the Lok Sabha?",
        "options": ["543", "545", "552", "500"],
        "answer": "552",
        "explanation": "Lok Sabha can have a maximum of 552 members: 530 from states, 20 from UTs, and 2 nominated Anglo-Indians (nomination provision lapsed in 2020).",
        "category": "Parliament",
    },
    {
        "q": "EVM stands for?",
        "options": [
            "Electronic Voting Machine",
            "Electoral Verification Module",
            "Electronic Voter Management",
            "Election Verification Mechanism",
        ],
        "answer": "Electronic Voting Machine",
        "explanation": "EVMs were first used on a pilot basis in Kerala in 1982 and became universal by 2004.",
        "category": "Voting Process",
    },
    {
        "q": "The Model Code of Conduct (MCC) comes into force when?",
        "options": [
            "On Election Day",
            "When election schedule is announced",
            "30 days before polling",
            "When nominations are filed",
        ],
        "answer": "When election schedule is announced",
        "explanation": "The MCC is triggered the moment the ECI announces the election schedule, limiting government actions.",
        "category": "Rules",
    },
    {
        "q": "VVPAT stands for?",
        "options": [
            "Voter Verified Paper Audit Trail",
            "Verified Voting Paper Attestation Tool",
            "Voter Verification Printed Audit Token",
            "Validated Voting Process Audit Trail",
        ],
        "answer": "Voter Verified Paper Audit Trail",
        "explanation": "VVPAT provides a paper slip confirmation after a vote is cast, enhancing transparency.",
        "category": "Voting Process",
    },
    {
        "q": "West Bengal has how many assembly constituencies?",
        "options": ["252", "294", "312", "280"],
        "answer": "294",
        "explanation": "West Bengal Legislative Assembly (Vidhan Sabha) has 294 seats.",
        "category": "State Elections",
    },
    {
        "q": "Which voter helpline number can citizens call for election-related queries?",
        "options": ["100", "1950", "1800", "112"],
        "answer": "1950",
        "explanation": "1950 is the National Voter Service Portal helpline operated by the ECI.",
        "category": "Resources",
    },
]

CATEGORY_COLORS = {
    "Constitution": "#4F6EF7",
    "Voting Process": "#00843D",
    "Documents": "#D95200",
    "Parliament": "#2D3561",
    "Rules": "#C62828",
    "State Elections": "#9C27B0",
    "Resources": "#0097A7",
}


def _reset_quiz() -> None:
    q_indices = list(range(len(QUIZ_QUESTIONS)))
    random.shuffle(q_indices)
    st.session_state["quiz_indices"] = q_indices[:7]
    st.session_state["quiz_current"] = 0
    st.session_state["quiz_score"] = 0
    st.session_state["quiz_answers"] = {}
    st.session_state["quiz_started"] = True
    st.session_state["quiz_done"] = False


def render_election_quiz() -> None:
    """Render the election knowledge quiz."""
    st.markdown("### 🎯 Election Knowledge Quiz")
    st.caption("Test your knowledge about Indian elections and democracy!")

    # ── Init state ────────────────────────────────────────────────────────────
    if "quiz_started" not in st.session_state:
        st.session_state["quiz_started"] = False
    if "quiz_done" not in st.session_state:
        st.session_state["quiz_done"] = False

    # ── Welcome screen ────────────────────────────────────────────────────────
    if not st.session_state.get("quiz_started"):
        st.markdown(
            """
            <div style="background:linear-gradient(135deg,#EEF2FF,#FFFFFF);
                        border-radius:16px;padding:28px;text-align:center;
                        border:1px solid #C5D0FF;box-shadow:0 4px 16px rgba(79,110,247,0.10);">
                <div style="font-size:3rem;margin-bottom:8px;">🗳️</div>
                <div style="font-weight:800;font-size:1.3rem;color:#1A1A2E;margin-bottom:8px;">
                    How well do you know Indian Elections?
                </div>
                <div style="color:#5C5C7A;font-size:0.9rem;margin-bottom:16px;">
                    7 questions · Multiple choice · Learn as you go
                </div>
                <div style="display:flex;justify-content:center;gap:16px;flex-wrap:wrap;font-size:0.8rem;color:#9090A8;">
                    <span>📜 Constitution</span>
                    <span>🗳️ Voting Process</span>
                    <span>🏛️ Parliament</span>
                    <span>📄 Documents</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🚀 Start Quiz", type="primary", use_container_width=True, key="start_quiz_btn"):
            _reset_quiz()
            st.rerun()
        return

    # ── Quiz done screen ──────────────────────────────────────────────────────
    if st.session_state.get("quiz_done"):
        score  = st.session_state.get("quiz_score", 0)
        total  = len(st.session_state.get("quiz_indices", []))
        pct    = (score / total) * 100 if total else 0

        if pct >= 80:
            emoji, label, color = "🏆", "Election Expert!", "#0E6B06"
        elif pct >= 50:
            emoji, label, color = "📚", "Good Citizen!", "#D95200"
        else:
            emoji, label, color = "🌱", "Keep Learning!", "#4F6EF7"

        st.markdown(
            f"""
            <div style="background:linear-gradient(135deg,{color}0D,#FFFFFF);
                        border-radius:16px;padding:28px;text-align:center;
                        border:2px solid {color}44;box-shadow:0 4px 16px {color}20;">
                <div style="font-size:4rem;">{emoji}</div>
                <div style="font-weight:900;font-size:1.5rem;color:{color};margin:8px 0;">{label}</div>
                <div style="font-size:3rem;font-weight:800;color:#1A1A2E;">{score}/{total}</div>
                <div style="color:#5C5C7A;font-size:0.9rem;margin-top:4px;">{pct:.0f}% correct</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()
        st.markdown("#### 📖 Review Your Answers")
        indices = st.session_state.get("quiz_indices", [])
        answers = st.session_state.get("quiz_answers", {})
        for idx in indices:
            q   = QUIZ_QUESTIONS[idx]
            ans = answers.get(idx)
            is_correct = ans == q["answer"]
            bg    = "#F0FAF0" if is_correct else "#FFEBEE"
            color = "#0E6B06" if is_correct else "#C62828"
            icon  = "✅" if is_correct else "❌"
            cat_color = CATEGORY_COLORS.get(q["category"], "#999")
            st.markdown(
                f"""
                <div style="background:{bg};border-radius:12px;padding:14px;
                            border-left:4px solid {color};margin-bottom:10px;">
                    <div style="display:flex;gap:8px;align-items:flex-start;">
                        <span style="font-size:1.1rem;">{icon}</span>
                        <div style="flex:1;">
                            <div style="font-weight:700;color:#1A1A2E;font-size:0.88rem;margin-bottom:4px;">
                                {q['q']}
                            </div>
                            <div style="font-size:0.78rem;margin-bottom:4px;">
                                Your answer: <b style="color:{color};">{ans if ans else "Not answered"}</b><br>
                                Correct: <b style="color:#0E6B06;">{q['answer']}</b>
                            </div>
                            <div style="font-size:0.75rem;color:#5C5C7A;font-style:italic;">
                                💡 {q['explanation']}
                            </div>
                        </div>
                        <span style="background:{cat_color}18;color:{cat_color};
                                     font-size:0.65rem;font-weight:700;padding:2px 8px;
                                     border-radius:20px;white-space:nowrap;">
                            {q['category']}
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.button("🔄 Play Again", type="primary", use_container_width=True, key="replay_btn"):
            _reset_quiz()
            st.rerun()
        return

    # ── Active quiz ───────────────────────────────────────────────────────────
    indices = st.session_state.get("quiz_indices", [])
    current = st.session_state.get("quiz_current", 0)

    if current >= len(indices):
        st.session_state["quiz_done"] = True
        st.rerun()
        return

    q_idx     = indices[current]
    question  = QUIZ_QUESTIONS[q_idx]
    total_qs  = len(indices)
    progress  = current / total_qs

    # Progress bar
    st.progress(progress, text=f"Question {current + 1} of {total_qs}")

    cat_color = CATEGORY_COLORS.get(question["category"], "#999")
    st.markdown(
        f"""
        <div style="background:#FAFAF8;border-radius:16px;padding:20px;
                    border:1px solid #E8E4DC;border-top:4px solid {cat_color};
                    margin-bottom:1rem;box-shadow:0 2px 8px rgba(0,0,0,0.05);">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
                <span style="background:{cat_color}18;color:{cat_color};font-size:0.72rem;
                             font-weight:700;padding:3px 10px;border-radius:20px;">
                    {question['category']}
                </span>
                <span style="color:#9090A8;font-size:0.78rem;">
                    Score: {st.session_state.get('quiz_score', 0)}/{current}
                </span>
            </div>
            <div style="font-weight:700;font-size:1.05rem;color:#1A1A2E;line-height:1.5;">
                {question['q']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Answer tracking
    already_answered = q_idx in st.session_state.get("quiz_answers", {})

    if not already_answered:
        for opt in question["options"]:
            if st.button(opt, key=f"q{q_idx}_opt_{opt}", use_container_width=True):
                if "quiz_answers" not in st.session_state:
                    st.session_state["quiz_answers"] = {}
                st.session_state["quiz_answers"][q_idx] = opt
                if opt == question["answer"]:
                    st.session_state["quiz_score"] = st.session_state.get("quiz_score", 0) + 1
                st.rerun()
    else:
        chosen = st.session_state["quiz_answers"][q_idx]
        for opt in question["options"]:
            is_correct = opt == question["answer"]
            is_chosen  = opt == chosen
            if is_correct:
                bg, border, text = "#E8F5E6", "#0E6B06", "#0E6B06"
                icon = "✅ "
            elif is_chosen:
                bg, border, text = "#FFEBEE", "#C62828", "#C62828"
                icon = "❌ "
            else:
                bg, border, text = "#F5F3EF", "#E8E4DC", "#9090A8"
                icon = ""
            st.markdown(
                f'<div style="background:{bg};border:2px solid {border};border-radius:10px;'
                f'padding:10px 16px;margin-bottom:6px;color:{text};font-weight:600;font-size:0.9rem;">'
                f'{icon}{opt}</div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            f'<div style="background:#EEF2FF;border-radius:10px;padding:12px;font-size:0.82rem;'
            f'color:#2D3561;border-left:4px solid #4F6EF7;margin-top:8px;">'
            f'💡 <b>Explanation:</b> {question["explanation"]}</div>',
            unsafe_allow_html=True,
        )

        btn_label = "Next Question →" if current < total_qs - 1 else "See Results 🏆"
        if st.button(btn_label, type="primary", use_container_width=True, key=f"next_q_{current}"):
            st.session_state["quiz_current"] = current + 1
            st.rerun()
