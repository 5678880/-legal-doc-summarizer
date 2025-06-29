from llama_index.llms.ollama import Ollama
import streamlit as st
import os
from legal_backend import load_document, summarize_document, highlight_clauses, answer_query
from datetime import datetime
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.let_it_rain import rain
from fpdf import FPDF
from pdf2image import convert_from_path
import json

# --- PAGE CONFIG ---
st.set_page_config(page_title="⚖️ Legal Document Assistant",
                   layout="wide", page_icon="⚖️")

# --- THEME ---
theme = st.sidebar.radio("Choose Theme:", ["🌞 Light", "🌙 Dark"], index=0)

if theme == "🌙 Dark":
    background_color = "#1e1e1e"
    text_color = "#f1f1f1"
    box_color = "#2c2c2c"
    border_color = "#888"
    input_bg = "#333"
else:
    background_color = "white"
    text_color = "black"
    box_color = "#f1f1f1"
    border_color = "#ccc"
    input_bg = "white"

st.markdown(f"""
<style>
    body {{ background-color: {background_color}; color: {text_color}; }}
    .stApp {{ background-color: {background_color}; color: {text_color}; }}
    .title {{ font-size: 42px; font-weight: bold; color: #3a86ff; padding-top: 20px; }}
    .section-header {{ font-size: 26px; font-weight: 600; color: {text_color}; margin-top: 30px; }}
    .question-box {{ border: 2px solid {border_color}; padding: 15px; border-radius: 12px; margin-top: 15px; color: {text_color}; }}
    .answer-box {{ background-color: {box_color}; border-left: 5px solid #3a86ff; padding: 15px; margin-top: 15px; border-radius: 8px; color: {text_color}; }}
    .image-preview {{ border: 1px dashed {border_color}; margin-top: 10px; padding: 10px; }}
    .hidden {{ display: none; }}
    input, textarea {{ background-color: {input_bg} !important; color: {text_color} !important; }}
</style>
""", unsafe_allow_html=True)

if "first_time" not in st.session_state:
    st.session_state.first_time = True
if "history" not in st.session_state:
    st.session_state.history = []

# --- LOGIN SYSTEM ---
USERS_FILE = "users.json"

if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users_db = json.load(f)
else:
    users_db = {
        "admin": {
            "password": "admin123",
            "is_admin": True
        },
        "shreya": {
            "password": "letmein123",
            "is_admin": False
        }
    }
    with open(USERS_FILE, "w") as f:
        json.dump(users_db, f)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

if not st.session_state.authenticated:
    st.title("🔐 Welcome to Legal Document Assistant")
    choice = st.radio("Choose an option:", ["Login", "Create Account"])

    if choice == "Create Account":
        st.session_state.show_signup = True
    else:
        st.session_state.show_signup = False

    if st.session_state.show_signup:
        st.subheader("📝 Create Your Account")
        with st.form("signup_form"):
            new_user = st.text_input("Choose a username")
            new_pass = st.text_input("Choose a password", type="password")
            signup_btn = st.form_submit_button("Create Account")
            if signup_btn:
                if new_user and new_pass:
                    if new_user in users_db:
                        st.warning(
                            "⚠️ Username already exists. Please choose another.")
                    else:
                        users_db[new_user] = {
                            "password": new_pass, "is_admin": False}
                        with open(USERS_FILE, "w") as f:
                            json.dump(users_db, f)
                        st.success("✅ Account created! Please login.")
                        st.rerun()
                else:
                    st.error("❌ Both fields are required.")
        st.stop()

    st.subheader("🔐 Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")

    if login_btn:
        user_data = users_db.get(username)

        if isinstance(user_data, dict) and password == user_data.get("password"):
            st.success(f"✅ Welcome, {username}!")
            st.session_state.authenticated = True
            st.session_state.user = username
            st.session_state.is_admin = user_data.get("is_admin", False)
            if st.session_state.first_time:
                rain(emoji="⚖️", font_size=32,
                     falling_speed=5, animation_length=2)
                st.session_state.first_time = False
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

    st.markdown("---")
    st.info("🔑 Forgot password? Please contact the app administrator to reset it.")
    st.stop()

# --- ADMIN DASHBOARD ---
if st.session_state.is_admin:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🛠️ Admin Tools")
    with st.sidebar.expander("🔁 Reset User Password"):
        user_to_reset = st.text_input("Username to reset")
        new_user_pass = st.text_input("New Password", type="password")
        if st.button("🔄 Reset Password"):
            if user_to_reset in users_db:
                users_db[user_to_reset]["password"] = new_user_pass
                with open(USERS_FILE, "w") as f:
                    json.dump(users_db, f)
                st.success(f"✅ Password reset for '{user_to_reset}'")
            else:
                st.error("❌ User not found")

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/ios-filled/100/scale.png", width=80)
    st.title("Legal AI Assistant ⚖️")
    st.markdown("Built using Ollama + Streamlit")
    st.markdown("---")
    uploaded_file = st.file_uploader(
        "📁 Upload (PDF, TXT, DOCX)", type=["pdf", "txt", "docx"])
    st.markdown("---")
    st.markdown("🔐 All processing is 100% local.\nNo data leaves your computer.")

# --- STANDALONE CHAT ---
st.markdown("<div class='section-header'>⚖️ Legal Aid: Ask a Legal Expert</div>",
            unsafe_allow_html=True)
st.markdown("Ask any question related to law, rights, contracts, or general legal topics. No document upload needed.")

general_llm = Ollama(model="llama3")

with stylable_container("chat_anything", css_styles=f"border: 1px solid {border_color}; padding: 20px; border-radius: 10px; background-color: {box_color};"):
    with st.form("chat_form"):
        general_q = st.text_input("📢 Type your legal question:")
        submitted = st.form_submit_button("Ask the Expert")
        if submitted and general_q.strip():
            with st.spinner("Thinking like a lawyer..."):
                prompt = f"""
You are a highly trained AI legal assistant. Please answer this question in a simple, legally accurate, and understandable way for the average user.

Question: {general_q}
"""
                try:
                    result = general_llm.complete(prompt)
                    st.session_state.history.append(
                        {"q": general_q, "a": result.text.strip()})
                    st.markdown(
                        f"<div class='answer-box'>{result.text.strip()}</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(
                        "⚠️ Something went wrong while generating the answer.")
                    st.exception(e)

# --- CHAT HISTORY ---
if st.session_state.history:
    st.markdown("### 💬 Chat History")
    for i, qa in enumerate(reversed(st.session_state.history[-5:]), 1):
        st.markdown(f"**Q{i}:** {qa['q']}")
        st.markdown(f"**A{i}:** {qa['a']}")

# --- MAIN APP ---
st.markdown("<div class='title'>📄 Legal Document Assistant</div>",
            unsafe_allow_html=True)

if not uploaded_file:
    st.info("📌 Please upload a legal document to begin.")
else:
    if uploaded_file.size > 5 * 1024 * 1024:
        st.error("❌ File too large. Maximum allowed is 5MB.")
    else:
        os.makedirs("data", exist_ok=True)
        file_path = os.path.join("data", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("✅ File uploaded successfully!")

        if uploaded_file.name.endswith(".pdf"):
            try:
                images = convert_from_path(
                    file_path, first_page=1, last_page=1)
                st.image(images[0], caption="📄 Document Preview",
                         use_column_width=True)
            except Exception:
                st.info("Preview not available for this file.")

        with st.spinner("📚 Reading document..."):
            try:
                docs = load_document()
            except Exception as e:
                st.error(f"❌ Could not load the document: {e}")
                st.stop()

        st.markdown(
            "<div class='section-header'>🔧 What would you like to do?</div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)

        if col1.button("📄 Summarize Document"):
            with st.spinner("Summarizing..."):
                summary = summarize_document(docs)
            st.subheader("📄 Summary")
            st.write(summary)
            os.makedirs("outputs", exist_ok=True)
            filename = f"outputs/summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, "w") as f:
                f.write(summary)
            st.download_button("⬇️ Download Summary",
                               summary, file_name="summary.txt")

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for line in summary.split('\n'):
                pdf.multi_cell(0, 10, line)
            pdf_path = filename.replace(".txt", ".pdf")
            pdf.output(pdf_path)
            with open(pdf_path, "rb") as f:
                st.download_button("⬇️ Export as PDF", f,
                                   file_name="summary.pdf")

        if col2.button("📌 Highlight Legal Clauses"):
            with st.spinner("Highlighting..."):
                clauses = highlight_clauses(docs)
            st.subheader("📌 Important Clauses")
            st.write(clauses)

        with col3.form("ask_form"):
            user_q = st.text_input("💬 Ask a legal question:")
            asked = st.form_submit_button("Ask")
            if asked and user_q.strip():
                with st.spinner("Answering..."):
                    ans = answer_query(docs, user_q)
                st.subheader("🧠 Answer")
                st.write(ans)
            elif asked:
                st.warning("⚠️ Please type a question.")

        if st.button("📊 Clause-by-Clause Breakdown"):
            with st.spinner("Breaking down..."):
                breakdown = answer_query(
                    docs, "Break this legal document into clauses and explain each.")
            st.subheader("📊 Clause Breakdown")
            st.write(breakdown)

        if st.button("🔄 Simplify Legal Jargon"):
            with st.spinner("Simplifying..."):
                simple_text = answer_query(
                    docs, "Rewrite this legal document in very simple, everyday language.")
            st.subheader("🪄 Simplified Document")
            st.write(simple_text)

        st.markdown("### 🗃️ Uploaded Document History")
        for file in os.listdir("data"):
            st.markdown(f"- {file}")

st.markdown("""---  
🔐 **Privacy Notice:** This app runs entirely on your device using Ollama. No files or data are uploaded to the cloud.
""")
