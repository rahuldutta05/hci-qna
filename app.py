import html
import random

import streamlit as st

from questions import MODULES, QUESTIONS

st.set_page_config(page_title="HCI Practice – BCSE415L", page_icon="🧠", layout="centered")

st.markdown(
    """
<style>
.opt{padding:14px 16px;border-radius:10px;margin:8px 0;border:2px solid #d0d5dd;font-size:1.02rem;}
.opt.correct{background:#e6f9ed;border-color:#16a34a;color:#14532d;font-weight:600;}
.opt.wrong{background:#fdecec;border-color:#dc2626;color:#7f1d1d;font-weight:600;}
.opt.neutral{background:#f8f9fb;color:#667085;}
.tag{display:inline-block;padding:2px 10px;border-radius:12px;background:#eef2ff;color:#3730a3;font-size:.8rem;}
@media (prefers-color-scheme: dark){
 .opt.neutral{background:#1f2430;color:#9aa4b2;border-color:#3a4150;}
 .opt.correct{background:#0f3d24;color:#bbf7d0;}
 .opt.wrong{background:#4a1515;color:#fecaca;}
 .tag{background:#312e81;color:#e0e7ff;}
}
</style>
""",
    unsafe_allow_html=True,
)

S = st.session_state
S.setdefault("run", None)


def start(label, module=None, shuffle_q=False):
    pool = [q for q in QUESTIONS if module is None or q["module"] == module]
    pool = pool[:]
    if shuffle_q:
        random.shuffle(pool)
    prepared = []
    for q in pool:
        opts = [(q["correct"], True), (q["wrong"], False)]
        random.shuffle(opts)
        prepared.append({**q, "opts": opts})
    S.run = prepared
    S.label = label
    S.i = 0
    S.answers = {}
    S.run_id = random.random()
    S.done = False


def choose(i, j):
    S.answers[i] = j


def menu():
    S.run = None
    S.done = False


# ---------------------------------------------------------------- HOME
if S.run is None:
    st.title("🧠 HCI Practice – BCSE415L")
    st.caption("Application-based, two-option MCQs · 7 modules × 10 questions")
    mode = st.radio("Choose a mode", ["📘 Module-wise (10 questions)", "📝 Full test (all 70 questions)"])
    shuffle_q = st.checkbox("Shuffle question order", value=False)
    if mode.startswith("📘"):
        m = st.selectbox("Module", list(MODULES), format_func=lambda k: f"Module {k}: {MODULES[k]}")
        if st.button("Start module", type="primary", use_container_width=True):
            start(f"Module {m}: {MODULES[m]}", m, shuffle_q)
            st.rerun()
    else:
        if st.button("Start 70-question test", type="primary", use_container_width=True):
            start("Full test (70 questions)", None, shuffle_q)
            st.rerun()
    st.stop()

run = S.run
n = len(run)

# ---------------------------------------------------------------- RESULT
if S.done:
    score = sum(1 for k, j in S.answers.items() if run[k]["opts"][j][1])
    st.title("Results")
    st.subheader(f"{S.label}")
    st.metric("Score", f"{score} / {n}", f"{round(100 * score / n)}%")
    st.progress(score / n)
    if score == n:
        st.balloons()
    wrong = [k for k, j in S.answers.items() if not run[k]["opts"][j][1]]
    if wrong:
        st.markdown("### Review your mistakes")
        for k in sorted(wrong):
            q = run[k]
            st.markdown(f"**Q{k+1}. {q['q']}**")
            st.markdown(f"<div class='opt wrong'>❌ Your answer: {html.escape(q['opts'][S.answers[k]][0])}</div>", unsafe_allow_html=True)
            ok = next(t for t, c in q["opts"] if c)
            st.markdown(f"<div class='opt correct'>✅ Correct: {html.escape(ok)}</div>", unsafe_allow_html=True)
            st.info(q["why"])
    c1, c2 = st.columns(2)
    if c1.button("🔁 Retry same set", use_container_width=True):
        start(S.label, None if "Full" in S.label else run[0]["module"], True)
        st.rerun()
    if c2.button("🏠 Main menu", use_container_width=True):
        menu()
        st.rerun()
    st.stop()

# ---------------------------------------------------------------- QUESTION
i = S.i
q = run[i]
answered = i in S.answers
score_now = sum(1 for k, j in S.answers.items() if run[k]["opts"][j][1])

with st.sidebar:
    st.markdown(f"**{S.label}**")
    st.progress(len(S.answers) / n, text=f"Answered {len(S.answers)}/{n}")
    st.metric("Correct so far", f"{score_now} / {len(S.answers)}")
    if st.button("🏠 Quit to menu", use_container_width=True):
        menu()
        st.rerun()

st.markdown(
    f"<span class='tag'>Module {q['module']} · {MODULES[q['module']]}</span>",
    unsafe_allow_html=True,
)
st.subheader(f"Question {i+1} of {n}")
st.write(q["q"])

if not answered:
    for j, (text, _) in enumerate(q["opts"]):
        st.button(
            f"{'AB'[j]}.  {text}",
            key=f"o_{S.run_id}_{i}_{j}",
            on_click=choose,
            args=(i, j),
            use_container_width=True,
        )
else:
    picked = S.answers[i]
    for j, (text, is_ok) in enumerate(q["opts"]):
        if is_ok:
            cls, icon = "correct", "✅"
        elif j == picked:
            cls, icon = "wrong", "❌"
        else:
            cls, icon = "neutral", ""
        st.markdown(
            f"<div class='opt {cls}'>{icon} {'AB'[j]}. {html.escape(text)}</div>",
            unsafe_allow_html=True,
        )
    if q["opts"][picked][1]:
        st.success("✅ Correct!")
    else:
        st.error("❌ Wrong answer")
    st.info(f"**Why:** {q['why']}")

st.write("")
c1, c2 = st.columns(2)
if c1.button("← Previous", disabled=i == 0, use_container_width=True):
    S.i -= 1
    st.rerun()
if i < n - 1:
    if c2.button("Next →", disabled=not answered, type="primary", use_container_width=True):
        S.i += 1
        st.rerun()
else:
    if c2.button("Finish 🏁", disabled=not answered, type="primary", use_container_width=True):
        S.done = True
        st.rerun()
