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
parser = JsonOutputParser()

prompt = PromptTemplate(
    input_variables=["resume_text", "job_description", "custom_prompt"],
    template="""
        You are an ATS (Applicant Tracking System) expert.

        Analyze the RESUME against the JOB DESCRIPTION and return a JSON object with exactly these REQUIRED keys:

        - "score": an integer from 0 to 100 representing the ATS match score
        - "strengths": array of strings — what the resume does well relative to the JD
        - "weaknesses": array of strings — gaps or misalignments between the resume and JD
        - "suggestions": array of strings — specific, actionable steps to improve the ATS score
        - "formatting_issues": array of strings — design or formatting elements that may hurt ATS parsing
        - "rewrites": array of objects, each with:
            - "original": the exact phrase or sentence quoted from the resume
            - "replacement": improved text that better aligns with the JD

        CUSTOM INSTRUCTIONS:
        {custom_prompt}

        If CUSTOM INSTRUCTIONS are provided (i.e. not empty):
        - Treat each instruction as an additional analysis task
        - For each instruction, add a NEW key to the JSON object:
            - The key name should be a short snake_case label summarizing the instruction
              (e.g., "tone_analysis", "missing_certifications", "keyword_density")
            - The value should be an array of strings with the findings for that instruction
        - Do NOT remove or modify the required keys above — only ADD new ones
        - If CUSTOM INSTRUCTIONS are empty or blank, return only the required keys

        JOB DESCRIPTION:
        {job_description}

        RESUME:
        {resume_text}

        Return ONLY the JSON object. No explanation, no markdown, no code fences.
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

    chain_extract = prompt | llm | parser
    res = chain_extract.invoke({
        "resume_text": resume_text,
        "job_description": job_description,
        "custom_prompt": custom_prompt
    })
    return res
