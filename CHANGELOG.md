# Changelog

## [Day 1] — 2026-07-25
### Setup & Core Build
- Created GitHub repo (applyiq)
- Set up Python virtual environment
- Installed dependencies: streamlit, pandas, supabase, bcrypt, spaCy, PyPDF2
- Created folder structure: app/, data/, docs/
- Built app/auth.py — Supabase login/signup
- Built app/tracker.py — CRUD for applications
- Built app/resume_tailor.py — NLP keyword extraction and match scoring
- Built app/analytics.py — stats, follow-up reminders, charts
- Built streamlit_app.py — full UI with 5 pages
- Dashboard, Add Application, My Applications, Resume Tailor, Analytics all working
- Supabase database set up with users and applications tables

## [Day 2] — 2026-07-26
### Resume Tailor Feature
- Fixed keyword extraction using whitelist approach
- Only shows real tech/professional skills as missing keywords
- Match score calculation using TF-IDF cosine similarity working
- Suggestions showing PLC, C++, mechanical, conveyor, project management for robotics JD
- Installed scikit-learn for match score calculation
- Cleared spaCy cache issues

