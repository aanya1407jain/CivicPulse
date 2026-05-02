"""
CivicPulse — Election Quiz Component
"""

from __future__ import annotations
import streamlit as st
import random
from components.language_selector import T

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
    "Constitution":    "#4F8EF7",
    "Voting Process":  "#27C96E",
    "Documents":       "#FF6B1A",
    "Parliament":      "#9BA3BC",
    "Rules":           "#F74F4F",
    "State Elections": "#C084FC",
    "Resources":       "#22D3EE",
}


def _reset_quiz() -> None:
    q_indices = list(range(len(QUIZ_QUESTIONS)))
    random.shuffle(q_indices)
    st.session_state["quiz_indices"] = q_indices[:7]
    st.session_state["quiz_current"] = 0
    st.session_state["quiz_score"]   = 0
    st.session_state["quiz_answers"] = {}
    st.session_state["quiz_started"] = True
    st.session_state["quiz_done"]    = False


def render_election_quiz() -> None:
    st.markdown(f"### 🎯 {T('Election Knowledge Quiz')}")
    st.caption(T("Test your knowledge about Indian elections and democracy!"))

    if "quiz_started" not in st.session_state:
        st.session_state["quiz_started"] = False
    if "quiz_done" not in st.session_state:
        st.session_state["quiz_done"] = False

    # ── Welcome screen ────────────────────────────────────────────────────────
    if not st.session_state.get("quiz_started"):
        headline    = T("How well do you know Indian Elections?")
        subheadline = T("7 questions · Multiple choice · Learn as you go")
        st.markdown(
            f"""
            <div style="background:linear-gradient(135deg,#1C2030,#141720);
                        border-radius:16px;padding:28px;text-align:center;
                        border:1px solid rgba(79,142,247,0.25);box-shadow:0 4px 16px rgba(0,0,0,0.4);">
                <div style="font-size:3rem;margin-bottom:8px;">🗳️</div>
                <div style="font-weight:800;font-size:1.3rem;color:#E8EAF0;margin-bottom:8px;">
                    {headline}
                </div>
                <div style="color:#9BA3BC;font-size:0.9rem;margin-bottom:16px;">
                    {subheadline}
                </div>
                <div style="display:flex;justify-content:center;gap:16px;flex-wrap:wrap;font-size:0.8rem;color:#5C6480;">
                    <span>📜 {T('Constitution')}</span>
                    <span>🗳️ {T('Voting Process')}</span>
                    <span>🏛️ {T('Parliament')}</span>
                    <span>📄 {T('Documents')}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(f"🚀 {T('Start Quiz')}", type="primary", use_container_width=True, key="start_quiz_btn"):
            _reset_quiz()
            st.rerun()
        return

    # ── Quiz done screen ──────────────────────────────────────────────────────
    if st.session_state.get("quiz_done"):
        score = st.session_state.get("quiz_score", 0)
        total = len(st.session_state.get("quiz_indices", []))
        pct   = (score / total) * 100 if total else 0

        if pct >= 80:
            emoji, label, color = "🏆", T("Election Expert!"),  "#27C96E"
        elif pct >= 50:
            emoji, label, color = "📚", T("Good Citizen!"),     "#FF6B1A"
        else:
            emoji, label, color = "🌱", T("Keep Learning!"),    "#4F8EF7"

        correct_label = T("correct")
        st.markdown(
            f"""
            <div style="background:linear-gradient(135deg,{color}18,#141720);
                        border-radius:16px;padding:28px;text-align:center;
                        border:2px solid {color}44;box-shadow:0 4px 24px {color}22;">
                <div style="font-size:4rem;">{emoji}</div>
                <div style="font-weight:900;font-size:1.5rem;color:{color};margin:8px 0;">{label}</div>
                <div style="font-size:3rem;font-weight:800;color:#E8EAF0;">{score}/{total}</div>
                <div style="color:#9BA3BC;font-size:0.9rem;margin-top:4px;">{pct:.0f}% {correct_label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()
        st.markdown(f"#### 📖 {T('Review Your Answers')}")
        indices = st.session_state.get("quiz_indices", [])
        answers = st.session_state.get("quiz_answers", {})
        your_answer_label   = T("Your answer")
        correct_label       = T("Correct")
        not_answered_label  = T("Not answered")

        for idx in indices:
            q          = QUIZ_QUESTIONS[idx]
            ans        = answers.get(idx)
            is_correct = ans == q["answer"]
            bg         = "rgba(39,201,110,0.10)" if is_correct else "rgba(247,79,79,0.10)"
            color      = "#27C96E" if is_correct else "#F74F4F"
            border_color = "#27C96E" if is_correct else "#F74F4F"
            icon       = "✅" if is_correct else "❌"
            cat_color  = CATEGORY_COLORS.get(q["category"], "#9BA3BC")
            q_text     = T(q["q"])
            exp_text   = T(q["explanation"])
            ans_text   = T(ans) if ans else not_answered_label
            corr_text  = T(q["answer"])
            cat_text   = T(q["category"])
            st.markdown(
                f"""
                <div style="background:{bg};border-radius:12px;padding:14px;
                            border-left:4px solid {border_color};margin-bottom:10px;">
                    <div style="display:flex;gap:8px;align-items:flex-start;">
                        <span style="font-size:1.1rem;">{icon}</span>
                        <div style="flex:1;">
                            <div style="font-weight:700;color:#E8EAF0;font-size:0.88rem;margin-bottom:4px;">
                                {q_text}
                            </div>
                            <div style="font-size:0.78rem;margin-bottom:4px;color:#9BA3BC;">
                                {your_answer_label}: <b style="color:{color};">{ans_text}</b><br>
                                {correct_label}: <b style="color:#27C96E;">{corr_text}</b>
                            </div>
                            <div style="font-size:0.75rem;color:#5C6480;font-style:italic;">
                                💡 {exp_text}
                            </div>
                        </div>
                        <span style="background:{cat_color}22;color:{cat_color};
                                     font-size:0.65rem;font-weight:700;padding:2px 8px;
                                     border-radius:20px;white-space:nowrap;border:1px solid {cat_color}44;">
                            {cat_text}
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.button(f"🔄 {T('Play Again')}", type="primary", use_container_width=True, key="replay_btn"):
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

    q_idx    = indices[current]
    question = QUIZ_QUESTIONS[q_idx]
    total_qs = len(indices)
    progress = current / total_qs

    question_label = T("Question")
    of_label       = T("of")
    score_label    = T("Score")

    st.progress(progress, text=f"{question_label} {current + 1} {of_label} {total_qs}")

    cat_color = CATEGORY_COLORS.get(question["category"], "#9BA3BC")
    q_text    = T(question["q"])
    cat_text  = T(question["category"])
    st.markdown(
        f"""
        <div style="background:#1C2030;border-radius:16px;padding:20px;
                    border:1px solid rgba(255,255,255,0.08);border-top:4px solid {cat_color};
                    margin-bottom:1rem;box-shadow:0 2px 12px rgba(0,0,0,0.3);">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
                <span style="background:{cat_color}22;color:{cat_color};font-size:0.72rem;
                             font-weight:700;padding:3px 10px;border-radius:20px;border:1px solid {cat_color}44;">
                    {cat_text}
                </span>
                <span style="color:#5C6480;font-size:0.78rem;">
                    {score_label}: {st.session_state.get('quiz_score', 0)}/{current}
                </span>
            </div>
            <div style="font-weight:700;font-size:1.05rem;color:#E8EAF0;line-height:1.5;">
                {q_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    already_answered = q_idx in st.session_state.get("quiz_answers", {})

    if not already_answered:
        for opt in question["options"]:
            opt_translated = T(opt)
            if st.button(opt_translated, key=f"q{q_idx}_opt_{opt}", use_container_width=True):
                if "quiz_answers" not in st.session_state:
                    st.session_state["quiz_answers"] = {}
                st.session_state["quiz_answers"][q_idx] = opt  # store original for comparison
                if opt == question["answer"]:
                    st.session_state["quiz_score"] = st.session_state.get("quiz_score", 0) + 1
                st.rerun()
    else:
        chosen          = st.session_state["quiz_answers"][q_idx]
        explanation_lbl = T("Explanation")
        for opt in question["options"]:
            is_correct = opt == question["answer"]
            is_chosen  = opt == chosen
            if is_correct:
                bg, border, text = "rgba(39,201,110,0.12)", "#27C96E", "#27C96E"
                icon = "✅ "
            elif is_chosen:
                bg, border, text = "rgba(247,79,79,0.12)", "#F74F4F", "#F74F4F"
                icon = "❌ "
            else:
                bg, border, text = "#1C2030", "rgba(255,255,255,0.08)", "#5C6480"
                icon = ""
            aria_pressed = "true" if is_chosen else "false"
            st.markdown(
                f'<div role="button" aria-pressed="{aria_pressed}" tabindex="0" '
                f'style="background:{bg};border:2px solid {border};border-radius:10px;'
                f'padding:10px 16px;margin-bottom:6px;color:{text};font-weight:600;font-size:0.9rem;">'
                f'{icon}{T(opt)}</div>',
                unsafe_allow_html=True,
            )

        explanation_text = T(question["explanation"])
        st.markdown(
            f'<div style="background:rgba(79,142,247,0.10);border-radius:10px;padding:12px;font-size:0.82rem;'
            f'color:#9BA3BC;border-left:4px solid #4F8EF7;margin-top:8px;">'
            f'💡 <b style="color:#E8EAF0;">{explanation_lbl}:</b> {explanation_text}</div>',
            unsafe_allow_html=True,
        )

        next_label = T("Next Question") + " →" if current < total_qs - 1 else T("See Results") + " 🏆"
        if st.button(next_label, type="primary", use_container_width=True, key=f"next_q_{current}"):
            st.session_state["quiz_current"] = current + 1
            st.rerun()
