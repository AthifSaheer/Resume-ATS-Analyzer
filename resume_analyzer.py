import os

from dotenv import load_dotenv
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

model = os.environ['MODEL']
temperature = os.environ['TEMPERATURE']
groq_api_key = os.environ['GROQ_API_KEY']

llm = ChatGroq(
    model=model,
    temperature=temperature,
    groq_api_key=groq_api_key
)

prompt = PromptTemplate(
    input_variables=["resume_text"],
    template="""
You are an ATS expert. Analyze the following resume and give:
1. Weaknesses (formatting, keyword usage, etc.)
2. Suggestions to improve ATS score
3. Remove unnecessary design elements

Resume:
{resume_text}
"""
)

def analyze_with_llm(resume_text):
    chain_extract = prompt | llm
    res = chain_extract.invoke(input={'resume_text': resume_text})
    return res.content
