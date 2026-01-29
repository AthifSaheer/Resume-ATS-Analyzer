import os

import streamlit as st
from dotenv import load_dotenv
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

model = st.secrets["MODEL"]
temperature = st.secrets["TEMPERATURE"]
groq_api_key = st.secrets["GROQ_API_KEY"]

llm = ChatGroq(
    model=model,
    temperature=temperature,
    groq_api_key=groq_api_key
)

prompt = PromptTemplate(
    input_variables=["resume_text", "job_description", "custom_prompt"],
    template="""
        You are an ATS (Applicant Tracking System) expert.

        Analyze the RESUME against the JOB DESCRIPTION and provide:

        1. ATS Match Score (0–100)
        2. Weaknesses of the resume compared to the JD
        3. Specific suggestions to improve the ATS score for THIS job
        4. Unnecessary design or formatting elements that may hurt ATS parsing

        JOB DESCRIPTION:
        {job_description}

        RESUME:
        {resume_text}

        {custom_prompt}
    """
)

def analyze_with_llm(resume_text, job_description, custom_prompt=None):
    if custom_prompt:
        custom_prompt = f"""
            ADDITIONAL USER INSTRUCTIONS:
            {custom_prompt}
        """
    else:
        custom_prompt = ""

    chain_extract = prompt | llm
    res = chain_extract.invoke({
        "resume_text": resume_text,
        "job_description": job_description,
        "custom_prompt": custom_prompt
    })
    return res.content
