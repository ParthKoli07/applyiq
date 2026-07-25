"""
resume_tailor.py
----------------
NLP-powered resume tailoring module for ApplyIQ.
Rewrites resume bullet points to better match a specific job description.

Author: Parth Koli
Project: ApplyIQ - Smart Internship Application Manager
"""

import spacy
import re
from collections import Counter

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

def extract_keywords_from_jd(jd_text):
    """Extract important keywords from job description"""
    doc = nlp(jd_text.lower())
    
    # Extract nouns and technical terms
    keywords = []
    for token in doc:
        if not token.is_stop and not token.is_punct and len(token.text) > 2:
            keywords.append(token.lemma_)
    
    # Get most frequent keywords
    keyword_counts = Counter(keywords)
    top_keywords = [word for word, count in keyword_counts.most_common(30)]
    
    return top_keywords

def extract_resume_text(resume_file, file_type):
    """Extract text from uploaded resume file"""
    try:
        if file_type == "application/pdf":
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(resume_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text
        else:
            return resume_file.read().decode("utf-8")
    except Exception as e:
        print(f"Error reading resume: {e}")
        return ""

def find_missing_keywords(jd_keywords, resume_text):
    """Find keywords in JD that are missing from resume"""
    resume_lower = resume_text.lower()
    missing = [kw for kw in jd_keywords if kw not in resume_lower]
    return missing

def calculate_match_score(jd_text, resume_text):
    """Calculate how well the resume matches the JD"""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    
    if not jd_text or not resume_text:
        return 0.0
    
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform([jd_text, resume_text])
        score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(score) * 100, 1)
    except:
        return 0.0

def tailor_resume(resume_text, jd_text):
    """
    Main function to tailor resume to job description.
    Returns tailored resume text with suggestions.
    """
    if not resume_text or not jd_text:
        return resume_text, [], 0.0
    
    # Step 1: Extract JD keywords
    jd_keywords = extract_keywords_from_jd(jd_text)
    
    # Step 2: Calculate match score
    match_score = calculate_match_score(jd_text, resume_text)
    
    # Step 3: Find missing keywords
    missing_keywords = find_missing_keywords(jd_keywords, resume_text)
    
    # Step 4: Generate suggestions
    suggestions = generate_suggestions(resume_text, missing_keywords, jd_keywords)
    
    return resume_text, suggestions, match_score

def generate_suggestions(resume_text, missing_keywords, jd_keywords):
    """Generate specific suggestions to improve resume"""
    suggestions = []
    
    if missing_keywords:
        suggestions.append({
            'type': 'missing_keywords',
            'title': '🔑 Missing Keywords',
            'description': f"Add these keywords from the JD to your resume:",
            'items': missing_keywords[:10]
        })
    
    # Check for quantifiable achievements
    numbers = re.findall(r'\d+', resume_text)
    if len(numbers) < 3:
        suggestions.append({
            'type': 'quantify',
            'title': '📊 Add Numbers',
            'description': 'Quantify your achievements with numbers',
            'items': [
                'Add percentage improvements (e.g. "improved performance by 40%")',
                'Add team sizes (e.g. "led a team of 5")',
                'Add project scale (e.g. "handled 10,000+ records")'
            ]
        })
    
    # Check resume length
    word_count = len(resume_text.split())
    if word_count < 200:
        suggestions.append({
            'type': 'length',
            'title': '📝 Expand Your Resume',
            'description': 'Your resume seems short',
            'items': [
                'Add more details to your project descriptions',
                'Include technical skills section',
                'Add certifications or courses'
            ]
        })
    
    return suggestions