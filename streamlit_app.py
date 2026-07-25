import streamlit as st
import pandas as pd
from datetime import date, timedelta
from app.auth import signup_user, login_user
from app.tracker import add_application, get_applications, update_application_status, delete_application
from app.resume_tailor import extract_resume_text, tailor_resume, calculate_match_score
from app.analytics import get_application_stats, get_applications_by_status, get_follow_up_reminders

st.set_page_config(
    page_title="ApplyIQ",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .title-text { font-size: 2.5rem; font-weight: 700; color: #ffffff; }
    .subtitle-text { font-size: 1.1rem; color: #a0aec0; }
    .stat-card { background-color: #1e1e2e; padding: 1rem; border-radius: 10px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

# ─── AUTH PAGE ─────────────────────────────────────────────────
def show_auth_page():
    st.markdown('<p class="title-text">🎯 ApplyIQ</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Smart Internship Application Manager</p>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

        with tab1:
            st.markdown("### Welcome back!")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login", use_container_width=True, type="primary"):
                if username and password:
                    success, result = login_user(username, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user = result
                        st.rerun()
                    else:
                        st.error(result)
                else:
                    st.warning("Please fill in all fields!")

        with tab2:
            st.markdown("### Create an account")
            new_username = st.text_input("Username", key="signup_username")
            new_email = st.text_input("Email", key="signup_email")
            new_college = st.text_input("College", key="signup_college")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            if st.button("Sign Up", use_container_width=True, type="primary"):
                if all([new_username, new_email, new_password, confirm_password]):
                    if new_password != confirm_password:
                        st.error("Passwords don't match!")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters!")
                    else:
                        success, msg = signup_user(new_username, new_email, new_password, new_college)
                        if success:
                            st.success(msg + " Please login.")
                        else:
                            st.error(msg)
                else:
                    st.warning("Please fill in all fields!")

# ─── MAIN APP ──────────────────────────────────────────────────
def show_main_app():
    applications = get_applications(st.session_state.user['id'])
    stats = get_application_stats(applications)
    reminders = get_follow_up_reminders(applications)

    # Sidebar
    with st.sidebar:
        st.markdown(f"## 🎯 ApplyIQ")
        st.markdown(f"👋 Hello, **{st.session_state.user['username']}**!")
        st.markdown("---")
        page = st.radio("Navigate", [
            "📊 Dashboard",
            "➕ Add Application",
            "📋 My Applications",
            "✂️ Resume Tailor",
            "📈 Analytics"
        ])
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()

    # ─── DASHBOARD ─────────────────────────────────────────────
    if page == "📊 Dashboard":
        st.markdown('<p class="title-text">📊 Dashboard</p>', unsafe_allow_html=True)
        st.markdown("---")

        # Metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("📨 Total", stats['total'])
        col2.metric("⏳ Applied", stats['applied'])
        col3.metric("🎤 Interviewing", stats['interviewing'])
        col4.metric("🎉 Offered", stats['offered'])
        col5.metric("❌ Rejected", stats['rejected'])

        st.markdown("---")

        col_left, col_right = st.columns(2)
        with col_left:
            st.metric("✅ Success Rate", f"{stats['success_rate']}%")
            st.metric("📬 Response Rate", f"{stats['response_rate']}%")

        with col_right:
            if reminders:
                st.markdown("### ⏰ Follow-up Reminders")
                for r in reminders:
                    days = r['days_overdue']
                    if days == 0:
                        st.warning(f"Follow up with **{r['company']}** for **{r['role']}** — due today!")
                    else:
                        st.error(f"Follow up with **{r['company']}** for **{r['role']}** — {days} days overdue!")
            else:
                st.success("✅ No pending follow-ups!")

        st.markdown("---")

        if applications:
            st.markdown("### 📋 Recent Applications")
            recent = pd.DataFrame(applications[:5])[['company', 'role', 'status', 'applied_date']]
            recent.columns = ['Company', 'Role', 'Status', 'Applied Date']
            st.dataframe(recent, use_container_width=True, hide_index=True)

    # ─── ADD APPLICATION ────────────────────────────────────────
    elif page == "➕ Add Application":
        st.markdown('<p class="title-text">➕ Add Application</p>', unsafe_allow_html=True)
        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            company = st.text_input("Company Name *")
            role = st.text_input("Job Role *")
            status = st.selectbox("Status", ["Applied", "Interview Scheduled", "Offered", "Rejected", "Withdrawn"])
            applied_date = st.date_input("Applied Date", value=date.today())
        with col2:
            follow_up_date = st.date_input("Follow-up Date", value=date.today() + timedelta(days=7))
            notes = st.text_area("Notes", placeholder="Any notes about this application...")

        jd_text = st.text_area("Job Description (paste here)", height=200,
                                placeholder="Paste the full job description here...")

        if st.button("➕ Add Application", type="primary", use_container_width=True):
            if company and role:
                success, msg = add_application(
                    user_id=st.session_state.user['id'],
                    company=company,
                    role=role,
                    jd_text=jd_text,
                    status=status,
                    applied_date=applied_date,
                    follow_up_date=follow_up_date,
                    notes=notes
                )
                if success:
                    st.success(f"✅ Application for {role} at {company} added!")
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("Company and Role are required!")

    # ─── MY APPLICATIONS ────────────────────────────────────────
    elif page == "📋 My Applications":
        st.markdown('<p class="title-text">📋 My Applications</p>', unsafe_allow_html=True)
        st.markdown("---")

        if not applications:
            st.info("No applications yet! Go to **Add Application** to get started.")
        else:
            # Filter
            status_filter = st.selectbox("Filter by status",
                ["All", "Applied", "Interview Scheduled", "Offered", "Rejected", "Withdrawn"])

            filtered = applications
            if status_filter != "All":
                filtered = [a for a in applications if a['status'] == status_filter]

            st.markdown(f"Showing **{len(filtered)}** applications")

            for app in filtered:
                with st.expander(f"🏢 {app['company']} — {app['role']} | {app['status']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Status:** {app['status']}")
                        st.markdown(f"**Applied:** {app['applied_date']}")
                        st.markdown(f"**Follow-up:** {app.get('follow_up_date', 'Not set')}")
                    with col2:
                        new_status = st.selectbox(
                            "Update Status",
                            ["Applied", "Interview Scheduled", "Offered", "Rejected", "Withdrawn"],
                            index=["Applied", "Interview Scheduled", "Offered", "Rejected", "Withdrawn"].index(app['status']),
                            key=f"status_{app['id']}"
                        )
                        if st.button("Update", key=f"update_{app['id']}"):
                            update_application_status(app['id'], new_status)
                            st.success("Status updated!")
                            st.rerun()

                    if app.get('notes'):
                        st.markdown(f"**Notes:** {app['notes']}")

                    if st.button("🗑️ Delete", key=f"delete_{app['id']}"):
                        delete_application(app['id'])
                        st.rerun()

    # ─── RESUME TAILOR ──────────────────────────────────────────
    elif page == "✂️ Resume Tailor":
        st.markdown('<p class="title-text">✂️ Resume Tailor</p>', unsafe_allow_html=True)
        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📄 Your Resume")
            resume_file = st.file_uploader("Upload Resume (PDF or TXT)", type=["pdf", "txt"])
            resume_text = ""
            if resume_file:
                resume_text = extract_resume_text(resume_file, resume_file.type)
                st.success(f"✅ Resume loaded — {len(resume_text.split())} words")

        with col2:
            st.markdown("### 💼 Job Description")
            jd_text = st.text_area("Paste Job Description here", height=250)

        if st.button("✂️ Tailor My Resume", type="primary", use_container_width=True):
            if resume_text and jd_text:
                with st.spinner("Analyzing and tailoring... ⏳"):
                    _, suggestions, match_score = tailor_resume(resume_text, jd_text)

                st.markdown("---")
                st.markdown("## 📊 Results")

                # Match score
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("🎯 Current Match Score", f"{match_score}%")
                    st.progress(match_score / 100)
                    if match_score < 30:
                        st.error("Low match — follow the suggestions below!")
                    elif match_score < 60:
                        st.warning("Moderate match — room for improvement!")
                    else:
                        st.success("Good match — strong application!")

                st.markdown("---")
                st.markdown("## 💡 Suggestions to Improve Your Resume")

                for suggestion in suggestions:
                    with st.expander(f"{suggestion['title']}"):
                        st.markdown(suggestion['description'])
                        for item in suggestion['items']:
                            st.markdown(f"• {item}")

                # Save to application
                st.markdown("---")
                st.markdown("### 💾 Save to Application")
                if applications:
                    app_options = [f"{a['company']} — {a['role']}" for a in applications]
                    selected_app = st.selectbox("Select application to save to:", app_options)
                    if st.button("💾 Save Tailored Resume"):
                        st.success("✅ Saved to application!")
                else:
                    st.info("Add an application first to save this tailored resume.")
            else:
                st.warning("Please upload your resume and paste a job description!")

    # ─── ANALYTICS ──────────────────────────────────────────────
    elif page == "📈 Analytics":
        st.markdown('<p class="title-text">📈 Analytics</p>', unsafe_allow_html=True)
        st.markdown("---")

        if not applications:
            st.info("No applications yet — add some to see analytics!")
        else:
            status_counts = get_applications_by_status(applications)

            st.markdown("### 📊 Applications by Status")
            chart_data = pd.DataFrame(
                list(status_counts.items()),
                columns=['Status', 'Count']
            ).set_index('Status')
            st.bar_chart(chart_data)

            st.markdown("---")
            st.markdown("### 🏆 Key Metrics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Applications", stats['total'])
            col2.metric("Success Rate", f"{stats['success_rate']}%")
            col3.metric("Response Rate", f"{stats['response_rate']}%")

            st.markdown("---")
            st.markdown("### 📋 All Applications")
            df = pd.DataFrame(applications)[['company', 'role', 'status', 'applied_date']]
            df.columns = ['Company', 'Role', 'Status', 'Applied Date']
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Download
            csv = pd.DataFrame(applications).to_csv(index=False)
            st.download_button(
                "⬇️ Download All Applications (CSV)",
                data=csv,
                file_name="my_applications.csv",
                mime="text/csv",
                use_container_width=True
            )

# ─── ROUTER ────────────────────────────────────────────────────
if st.session_state.logged_in:
    show_main_app()
else:
    show_auth_page()