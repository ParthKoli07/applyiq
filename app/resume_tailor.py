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


CUSTOM_STOP_WORDS = {
    'job', 'work', 'need', 'use', 'new', 'good', 'great', 'san', 'jose',
    'california', 'york', 'texas', 'india', 'remote', 'hybrid',
    'salary', 'benefit', 'degree', 'bachelor', 'master', 'year', 'experience',
    'company', 'team', 'role', 'position', 'opportunity', 'candidate',
    'skill', 'ability', 'knowledge', 'strong', 'excellent', 'preferred',
    'required', 'plus', 'bonus', 'base', 'range', 'incentive', 'revenue',
    'sale', 'sell', 'client', 'customer', 'business', 'market', 'product',
    'day', 'time', 'apply', 'please', 'form', 'may', 'also', 'full', 'onsite'
}

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

TECH_SKILLS_WHITELIST = {
    'python', 'java', 'javascript', 'c++', 'c#', 'typescript', 'scala', 'golang', 'rust', 'php', 'ruby',
    'react', 'angular', 'vue', 'node', 'django', 'flask', 'fastapi', 'spring',
    'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 'elasticsearch',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins',
    'machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow', 'pytorch',
    'pandas', 'numpy', 'scikit', 'matplotlib', 'tableau', 'power bi',
    'git', 'linux', 'bash', 'api', 'rest', 'graphql', 'microservices', 'agile', 'scrum',
    'robotics', 'automation', 'plc', 'ros', 'embedded', 'arduino', 'raspberry',
    'mechanical', 'electrical', 'circuit', 'sensor', 'actuator', 'vision',
    'conveyor', 'integration', 'deployment', 'testing', 'debugging',
    'project management', 'communication', 'leadership', 'training',
    'data analysis', 'data science', 'data engineering', 'etl', 'pipeline',
    'cybersecurity', 'networking', 'cloud', 'devops', 'mlops',
    'mobile', 'android', 'ios', 'flutter', 'react native',
    'figma', 'jira', 'confluence', 'notion', 'slack'
}

def extract_keywords_from_jd(jd_text):
    """Extract important tech keywords from job description using whitelist"""
    jd_lower = jd_text.lower()
    
    found_skills = []
    for skill in TECH_SKILLS_WHITELIST:
        if skill in jd_lower:
            found_skills.append(skill)
    
    return found_skills

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