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

if st.button("Submit") and uploaded_file:
    with st.spinner("Extracting text..."):
        text = extract_text_from_pdf(uploaded_file)
    
    st.subheader("🧠 AI Suggestions")
    with st.spinner("Analyzing with LLM..."):
        suggestions = analyze_with_llm(text, jd, custom_prompt)

    def render_json_ui(ai_response):
        try:
            data = ai_response
        except:
            st.error("AI response is not valid JSON.")
            st.code(ai_response)
            return

        if "score" in data:
            score = data["score"]
            col1, col2, col3 = st.columns([2,1,1])

            with col1:
                if score < 50:
                    st.error(f"📊 ATS Match Score: {score}/100")
                elif score < 75:
                    st.warning(f"📊 ATS Match Score: {score}/100")
                else:
                    st.success(f"📊 ATS Match Score: {score}/100")

        st.divider()

        for key, value in data.items():
            if key == "score":
                continue

            title = key.replace("_", " ").title()
            st.subheader(f"📌 {title}")

            if isinstance(value, list):
                if key == "rewrites":
                    for i, item in enumerate(value):
                        with st.expander(f"Rewrite Suggestion {i+1}"):
                            st.markdown("**Original Text**")
                            st.code(item.get("original", ""))

                            st.markdown("**Improved Version**")
                            st.success(item.get("replacement", ""))

                elif key == "missing_keywords":
                    cols = st.columns(4)

                    for i, keyword in enumerate(value):
                        cols[i % 4].markdown(
                            f"""
                            <div style="
                                padding:8px;
                                border-radius:8px;
                                text-align:center;
                                font-weight:600;">
                            {keyword}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    for item in value:
                        st.markdown(f"- {item}")
            elif isinstance(value, str):
                st.write(value)
            elif isinstance(value, dict):
                st.json(value)

            st.divider()    
    
    render_json_ui(suggestions)

    # st.subheader("📈 ATS Score")
    # score = score_resume(text)
    # st.metric("ATS Compatibility Score", f"{score}%")

    # if score < 70:
    #     st.warning("Your resume might not pass most ATS filters. Try improving based on the above suggestions.")
    # else:
    #     st.success("Looks good! Minor improvements may further help.")
