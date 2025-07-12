# ---------------- ⬇  app.py (TOP) ⬇ ----------------
from llama_index.llms.ollama import Ollama
import streamlit as st
import os
import json
import random
import requests
from legal_backend import (
    load_document, summarize_document, highlight_clauses, answer_query,
    clause_breakdown, simplify_legal_jargon, extract_entities,
    compare_documents,
)
from streamlit_extras.let_it_rain import rain
from streamlit_lottie import st_lottie
from fpdf import FPDF
from pdf2image import convert_from_path
from datetime import datetime

# ── PAGE CONFIG ─────────────────────────────────────
st.set_page_config(page_title="⚖️ Legal Document Assistant",
                   layout="wide", page_icon="⚖️")

theme = st.sidebar.radio("Choose Theme:", ["🌞 Light", "🌙 Dark"], 0)
is_dark = theme == "🌙 Dark"

# Modern, accessible theme variables
background_color = "#1e1e1e" if is_dark else "#ffffff"
text_color = "#f0f0f0" if is_dark else "#1a1a1a"
box_color = "#2a2a2a" if is_dark else "#f7f7f7"
border_color = "#3a86ff" if is_dark else "#1f4ed8"
input_bg = "#2a2a2a" if is_dark else "#ffffff"

# ── GLOBAL STYLES  (wallpaper + core CSS) ───────────
# Load fonts
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Merriweather:wght@700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# Inject full CSS
st.markdown(f"""
<style>
/* Base app layout */
.stApp {{
    font-family: 'Inter', sans-serif;
    background-color: {background_color};
    background-image: url('https://cdn.pixabay.com/photo/2017/01/10/19/05/scales-of-justice-1961451_1280.jpg');
    background-size: cover;
    background-attachment: fixed;
    background-position: center;
    background-repeat: no-repeat;
    min-height: 100vh;
    color: {text_color};
}}

/* Dim overlay */
.stApp::before {{
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: {"rgba(0, 0, 0, 0.75)" if is_dark else "rgba(255, 255, 255, 0.35)"};
    z-index: -1;
    backdrop-filter: blur(4px);
}}

/* Typography */
h1, h2, h3, h4, h5, h6, .title {{
    font-family: 'Merriweather', serif;
    font-weight: 700;
    color: {text_color};
}}

.title {{
    font-size: 2.8rem;
    padding-top: 25px;
    padding-bottom: 10px;
}}

.section-header {{
    font-size: 1.6rem;
    font-family: 'Merriweather', serif;
    font-weight: 700;
    border-bottom: 2px solid #3a86ff;
    padding-bottom: 6px;
    margin-top: 30px;
    margin-bottom: 20px;
}}

body, label, input, textarea, select, p, span {{
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    letter-spacing: 0.3px;
    line-height: 1.6;
    color: {text_color};
}}

/* Inputs and Textareas */
input, textarea, select {{
    background-color: {input_bg};
    color: {text_color};
    border: 1.5px solid {border_color};
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 1rem;
}}

input:focus, textarea:focus, select:focus {{
    outline: none;
    border-color: #3a86ff;
    box-shadow: 0 0 6px #3a86ff;
}}

/* Question and Answer boxes */
.question-box {{
    border: 2px solid {border_color};
    padding: 18px;
    border-radius: 12px;
    margin-top: 20px;
    background-color: {"rgba(255, 255, 255, 0.1)" if is_dark else "rgba(255, 255, 255, 0.15)"};
    backdrop-filter: blur(6px);
}}

.answer-box {{
    background: none;
    border: none;
    margin-top: 10px;
    font-size: 1rem;
    line-height: 1.6;
    color: {text_color};
    white-space: pre-wrap;
}}

/* Buttons */
button[kind="primary"], .stButton>button {{
    background-color: {"#3a86ff" if is_dark else "#1f4ed8"};
    color: white;
    font-weight: bold;
    border-radius: 8px;
    border: none;
    transition: all 0.3s ease;
}}

button[kind="primary"]:hover, .stButton>button:hover {{
    background-color: {"#559aff" if is_dark else "#1d3fcf"};
}}

/* Scrollbars */
textarea::-webkit-scrollbar, input::-webkit-scrollbar {{
    width: 8px;
}}
textarea::-webkit-scrollbar-thumb, input::-webkit-scrollbar-thumb {{
    background-color: #3a86ff;
    border-radius: 10px;
}}

/* --- 🔧 Dropdown Fix Starts Here --- */
div[data-baseweb="select"] {{
    min-height: 48px;
    padding: 2px 6px;
    display: flex;
    align-items: center;
    border-radius: 10px;
    background-color: {input_bg};
    border: 1.5px solid {border_color};
}}

div[data-baseweb="select"] > div {{
    padding: 0px 10px !important;
    font-size: 1rem;
    display: flex;
    align-items: center;
    min-height: 40px;
    color: {text_color};
}}

div[data-baseweb="select"] div[role="button"] {{
    padding: 6px 10px !important;
    border-radius: 8px;
    display: flex;
    align-items: center;
}}

div[data-baseweb="select"] svg {{
    transform: scale(1.1);
    margin-left: auto;
    margin-right: 10px;
    color: {text_color};
}}

div[data-baseweb="menu"] {{
    background-color: {input_bg};
    color: {text_color};
    border-radius: 8px;
}}
/* --- 🔧 Dropdown Fix Ends Here --- */

/* Responsive typography */
@media (max-width: 768px) {{
    .title {{
        font-size: 2.2rem;
        padding-top: 15px;
    }}
    .section-header {{
        font-size: 1.3rem;
    }}
    .question-box, .answer-box {{
        padding: 14px;
        font-size: 1rem;
    }}
}}
</style>
""", unsafe_allow_html=True)

# ── ONE‑TIME  LOTTIE  MASCOT ────────────────────────


def load_lottie(url: str):
    try:
        r = requests.get(url, timeout=4)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


if st.session_state.get("first_time", True):
    lottie_json = load_lottie(
        "https://assets7.lottiefiles.com/packages/lf20_1pxqjqps.json")
    if lottie_json:
        st_lottie(lottie_json, height=120, key="gavel")
    st.session_state.first_time = False

# ========== SESSION STATE & AUTH  (unchanged) ==============================
for k, v in {"history": [], "authenticated": False, "user": None,
             "is_admin": False, "show_signup": False}.items():
    st.session_state.setdefault(k, v)

USERS_FILE = "users.json"
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({"admin": {"password": "admin123", "is_admin": True}}, f)
with open(USERS_FILE) as f:
    users_db = json.load(f)

# ---------------- LOGIN / SIGN‑UP CARD -------------------------------------
if not st.session_state.authenticated:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    st.title("🔐 Welcome to Legal Document Assistant")
    choice = st.radio("Choose an option:", ["Login", "Create Account"])
    st.session_state.show_signup = choice == "Create Account"

    if st.session_state.show_signup:
        st.subheader("📝 Create Account")
        with st.form("signup_form"):
            new_user = st.text_input("Username")
            new_pass = st.text_input("Password", type="password")
            if st.form_submit_button("Create Account"):
                if new_user in users_db:
                    st.warning("⚠️ Username exists.")
                elif new_user and new_pass:
                    users_db[new_user] = {
                        "password": new_pass, "is_admin": False}
                    with open(USERS_FILE, "w") as f:
                        json.dump(users_db, f)
                    st.session_state.update(authenticated=True, user=new_user)
                    st.success(f"✅ Account created: {new_user}")
                    rain(emoji="⚖️", font_size=32,
                         falling_speed=5, animation_length=2)
                    st.rerun()
    else:
        st.subheader("🔐 Login")
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                data = users_db.get(u)
                if data and p == data["password"]:
                    st.session_state.update(
                        authenticated=True, user=u, is_admin=data.get("is_admin", False))
                    st.success(f"✅ Welcome, {u}!")
                    rain(emoji="⚖️", font_size=32,
                         falling_speed=5, animation_length=2)
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ---------------- SIDEBAR & REST OF APP (unchanged) ------------------------
#   (leave all your existing code here)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/ios-filled/100/scale.png", width=80)
    st.title("Legal AI Assistant ⚖️")
    uploaded_file = st.file_uploader(
        "📁 Upload Document (PDF/TXT/DOCX)", type=["pdf", "txt", "docx"])
    st.markdown("🔐 100% Local: No data leaves your computer")

# --- TITLE ---
st.markdown("<div class='title'>📄 Legal Document Assistant</div>",
            unsafe_allow_html=True)
st.markdown("### ❓ Ask a Legal Question")

with st.form("universal_ask_form"):
    question_type = st.selectbox(
        "📂 Question Type", ["Document-Based", "General"], key="qtype_top")
    user_q = st.text_input(
        "💬 Ask your question", placeholder="Ask about a section, clause, or topic...")
    ask_now = st.form_submit_button("Ask")

if ask_now and user_q.strip():
    st.subheader("🧠 Answer")
    if question_type == "Document-Based":
        if uploaded_file:
            docs = load_document(os.path.join("data", uploaded_file.name))
            st.write(answer_query(docs, user_q))
        else:
            st.warning(
                "📁 Please upload a document first for document-based questions.")
    else:
        general_llm = Ollama(model="llama3")
        with st.spinner("Thinking..."):
            prompt = f"""
You are a witty but ethical legal assistant AI. Answer the following question with a mix of accuracy and mild wit, without encouraging illegal behavior.

If the question involves criminal activity, explain:
- Applicable IPC sections
- Legal consequences
- That this is not legal advice

End with:
📌 Disclaimer: This response is for educational purposes only. Please consult a licensed legal professional.

User's Question: {user_q}
AI:"""
            result = general_llm.complete(prompt)
            st.markdown(
                f"""<div class='answer-box'>{result.text.strip()}</div>""",
                unsafe_allow_html=True
            )


# ... all your import and config code remains unchanged above ...
# --- MAIN LOGIC ---
if uploaded_file:
    if uploaded_file.size > 5 * 1024 * 1024:
        st.error("❌ File too large. Max is 5MB.")
    else:
        os.makedirs("data", exist_ok=True)
        file_path = os.path.join("data", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("✅ File uploaded!")
        docs = load_document(file_path)

        if "doc_id" not in st.session_state:
            st.session_state.doc_id = uploaded_file.name

        # --- TOGGLE STATE INIT ---
        toggle_keys = {
            "preview": "toggle_preview",
            "summary": "toggle_summary",
            "clauses": "toggle_clauses",
            "breakdown": "toggle_breakdown",
            "simplify": "toggle_simplify",
            "entities": "toggle_entities"
        }

        for k in toggle_keys.values():
            if k not in st.session_state:
                st.session_state[k] = False

        # --- INIT RESULT CACHE FLAGS ---
        cache_keys = {
            "summary_result": "run_summary",
            "highlight_result": "run_highlight",
            "breakdown_result": "run_breakdown",
            "simplified_output": "run_simplify",
            "entities_result": "run_entities"
        }

        for k in cache_keys.values():
            if k not in st.session_state:
                st.session_state[k] = False

        if st.sidebar.button("🔄 Reset View"):
            for key in toggle_keys.values():
                st.session_state[key] = False

        col1, col2, col3 = st.columns(3)

        # --- PREVIEW BUTTON ---
        if uploaded_file.name.endswith(".pdf"):
            if st.button("👁️ Preview First Page", help="Show the first page of the uploaded PDF"):
                st.session_state.toggle_preview = not st.session_state.toggle_preview

            if st.session_state.toggle_preview:
                try:
                    image = convert_from_path(
                        file_path, first_page=1, last_page=1)
                    st.image(image[0], caption="📄 Preview (Page 1)",
                             use_column_width=True)
                except Exception:
                    st.warning(
                        "⚠️ Preview not available — ensure Poppler is installed.")

        if not docs:
            st.error("❌ Could not extract text. Try a different document.")
            st.stop()
        # --- SUMMARIZE ---
        if col1.button("📄 Summarize Document", help="Generate a short summary of the uploaded legal doc"):
            st.session_state.run_summary = True
            st.session_state.toggle_summary = True

        if st.session_state.run_summary:
            with st.spinner("Summarizing..."):
                summary = summarize_document(docs)
                if not summary.strip():
                    st.error("❌ Summarization failed.")
                    st.stop()
                st.session_state.summary_result = summary
                st.session_state.run_summary = False

        if st.session_state.toggle_summary and "summary_result" in st.session_state:
            summary = st.session_state.summary_result
            st.subheader("📄 Summary")
            st.text_area("📄 Summary Output", summary,
                         height=300, key="summary_box")
            st.download_button("⬇️ Download TXT", summary,
                               file_name="summary.txt")
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for line in summary.split('\n'):
                safe_text = line.encode("latin-1", "replace").decode("latin-1")
                pdf.multi_cell(0, 10, safe_text)
            os.makedirs("outputs", exist_ok=True)
            pdf_path = "outputs/summary.pdf"
            pdf.output(pdf_path)
            with open(pdf_path, "rb") as f:
                st.download_button("⬇️ Export as PDF", f,
                                   file_name="summary.pdf")

        st.markdown("---")

        # --- HIGHLIGHT CLAUSES ---
        if col2.button("📌 Highlight Clauses", help="Find key legal clauses in the document"):
            st.session_state.run_highlight = True
            st.session_state.toggle_clauses = True

        if st.session_state.run_highlight:
            with st.spinner("Extracting clauses..."):
                st.session_state.highlight_result = highlight_clauses(docs)
                st.session_state.run_highlight = False

        if st.session_state.toggle_clauses and "highlight_result" in st.session_state:
            st.subheader("📌 Legal Clauses")
            st.write(st.session_state.highlight_result)

        st.markdown("---")

        # --- CLAUSE BREAKDOWN ---
        if st.button("📊 Clause Breakdown", help="Break down complex clauses into understandable parts"):
            st.session_state.run_breakdown = True
            st.session_state.toggle_breakdown = True

        if st.session_state.run_breakdown:
            with st.spinner("Analyzing clauses..."):
                st.session_state.breakdown_result = clause_breakdown(docs)
                st.session_state.run_breakdown = False

        if st.session_state.toggle_breakdown and "breakdown_result" in st.session_state:
            st.subheader("📊 Breakdown")
            st.write(st.session_state.breakdown_result)

        st.markdown("---")

        # --- SIMPLIFY LEGAL JARGON ---
        if st.button("🔄 Simplify Legal Jargon", help="Convert legal language to plain English"):
            st.session_state.run_simplify = True
            st.session_state.toggle_simplify = True

        if st.session_state.run_simplify:
            with st.spinner("Simplifying..."):
                st.session_state.simplified_output = simplify_legal_jargon(
                    docs)
                st.session_state.run_simplify = False

        if st.session_state.toggle_simplify and "simplified_output" in st.session_state:
            st.subheader("🪄 Simplified Version")
            st.write(st.session_state.simplified_output)

        st.markdown("---")

        # --- EXTRACT ENTITIES ---
        if st.button("🔍 Extract Entities", help="Identify names, organizations, dates, etc. from the document"):
            st.session_state.run_entities = True
            st.session_state.toggle_entities = True

        if st.session_state.run_entities:
            with st.spinner("Identifying entities..."):
                try:
                    st.session_state.entities_result = extract_entities(docs)
                except Exception as e:
                    st.session_state.entities_result = f"❌ Failed to extract entities: {e}"
                st.session_state.run_entities = False

        if st.session_state.toggle_entities and "entities_result" in st.session_state:
            st.subheader("🔍 Named Entities")
            st.write(st.session_state.entities_result)

        st.markdown("---")

        # --- EXPORT HIGHLIGHTED PDF ---
        if st.button("📤 Export Highlighted PDF", key="export_pdf_main", help="Download a version of the PDF with clause highlights"):
            st.subheader("📤 Export PDF with Highlights")
            with st.spinner("Generating highlighted PDF..."):
                try:
                    export_path = export_highlighted_pdf(docs, file_path)
                    with open(export_path, "rb") as f:
                        st.download_button(
                            "⬇️ Download Highlighted PDF", f, file_name="highlighted_output.pdf")
                except Exception as e:
                    st.error(f"❌ Could not export PDF: {e}")

# --- COMPARE TWO DOCS SECTION ---
with st.expander("🆚 Compare Two Docs"):
    col1, col2 = st.columns(2)
    file1 = col1.file_uploader("📄 First Document", type=[
                               "pdf", "txt", "docx"], key="comp1")
    file2 = col2.file_uploader("📄 Second Document", type=[
                               "pdf", "txt", "docx"], key="comp2")

    if file1 and file2:
        file_path1 = os.path.join("data", file1.name)
        file_path2 = os.path.join("data", file2.name)
        with open(file_path1, "wb") as f:
            f.write(file1.getbuffer())
        with open(file_path2, "wb") as f:
            f.write(file2.getbuffer())

        if "last_comp1" not in st.session_state or st.session_state.last_comp1 != file1.name:
            st.session_state.docs1 = load_document(file_path1)
            st.session_state.last_comp1 = file1.name

        if "last_comp2" not in st.session_state or st.session_state.last_comp2 != file2.name:
            st.session_state.docs2 = load_document(file_path2)
            st.session_state.last_comp2 = file2.name

        docs1 = st.session_state.docs1
        docs2 = st.session_state.docs2

        if st.button("🔍 Compare Documents"):
            st.subheader("📋 Comparison Result")
            with st.spinner("Analyzing differences..."):
                try:
                    result = compare_documents(docs1, docs2)
                    st.write(result)
                except Exception as e:
                    st.error(f"❌ Comparison failed: {e}")

# --- CHAT HISTORY (toggle) ---
with st.expander("💬 Chat History"):
    history = st.session_state.get("history", [])
    if not history:
        st.write("No chat yet.")
    else:
        for q, a in history:
            st.markdown(f"**Q:** {q}")
            st.markdown(f"**A:** {a}")

# --- DOCUMENT HISTORY as dropdown ---
with st.expander("🗂️ Document History"):
    if os.path.exists("data"):
        for file in os.listdir("data"):
            st.markdown(f"- {file}")
    else:
        st.write("No documents uploaded yet.")

# --- FOOTER FACT ---
st.markdown("### ⚖️ Daily Legal Fact")
st.info(random.choice([
    "🧠 Article 21 guarantees Right to Life.",
    "📜 Indian Contract Act, 1872 governs contracts.",
    "👨‍⚖️ Supreme Court of India began in 1950.",
    "🏛️ Habeas Corpus protects from arrest.",
    "📖 Minors cannot sign legal contracts."
]))
