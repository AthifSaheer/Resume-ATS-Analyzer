import streamlit as st
from utils import extract_text_from_pdf, score_resume
from resume_analyzer import analyze_with_llm

st.set_page_config(page_title="Resume ATS Analyzer", layout="centered")

st.title("📄 Resume ATS Analyzer")
st.markdown("Upload your resume and get analysis based on **ATS (Applicant Tracking Systems)** best practices.")

uploaded_file = st.file_uploader("Upload your resume (PDF format)", type=["pdf"])

if uploaded_file:
    with st.spinner("Extracting text..."):
        text = extract_text_from_pdf(uploaded_file)

    st.subheader("📈 ATS Score")
    score = score_resume(text)
    st.metric("ATS Compatibility Score", f"{score}%")

    st.subheader("🧠 AI Suggestions")
    with st.spinner("Analyzing with LLM..."):
        suggestions = analyze_with_llm(text)

    st.text_area("🔍 Analysis Result", suggestions, height=300)

    if score < 70:
        st.warning("Your resume might not pass most ATS filters. Try improving based on the above suggestions.")
    else:
        st.success("Looks good! Minor improvements may further help.")
