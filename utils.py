from pdfminer.high_level import extract_text
import re

def extract_text_from_pdf(pdf_file):
    return extract_text(pdf_file)

def score_resume(text):
    score = 0
    total = 7

    if "experience" in text.lower(): score += 1
    if "education" in text.lower(): score += 1
    if "skills" in text.lower(): score += 1
    if len(text.split()) > 300: score += 1  # resume should be detailed
    if re.search(r'[•\-*]\s', text): score += 1  # bullet points
    if len(text) < 5000: score += 1  # not overloaded
    if re.search(r'(pdf|docx|txt)', text.lower()): score += 1  # file type mentioned

    return round((score / total) * 100, 2)
