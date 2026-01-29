import streamlit as st
from utils import extract_text_from_pdf, score_resume
from resume_analyzer import analyze_with_llm

st.set_page_config(page_title="Resume ATS Analyzer", layout="centered")

st.title("📄 Resume ATS Analyzer")
st.markdown("Upload your resume and get analysis based on **ATS (Applicant Tracking Systems)** best practices.")

uploaded_file = st.file_uploader("Upload your resume (PDF format)", type=["pdf"])
jd = st.text_area(
    label="Enter Job Description",
    height=300,
    placeholder="Paste or type the job description here..."
)
custom_prompt = st.text_area(
    label="Custom Prompt",
    height=100,
    placeholder="Add your custom prompt here..."
)

if st.button("Submit") and uploaded_file and jd:
    with st.spinner("Extracting text..."):
        text = extract_text_from_pdf(uploaded_file)
    
    st.subheader("🧠 AI Suggestions")
    with st.spinner("Analyzing with LLM..."):
        suggestions = analyze_with_llm(text, jd, custom_prompt)

    st.text_area("🔍 Analysis Result", suggestions, height=300)
    
    # st.subheader("📈 ATS Score")
    # score = score_resume(text)
    # st.metric("ATS Compatibility Score", f"{score}%")

    # if score < 70:
    #     st.warning("Your resume might not pass most ATS filters. Try improving based on the above suggestions.")
    # else:
    #     st.success("Looks good! Minor improvements may further help.")
