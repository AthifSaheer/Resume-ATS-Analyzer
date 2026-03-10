import streamlit as st
import json
import pandas as pd
from datetime import datetime
from crud import (
    get_all_company_tracks,
    get_company_track_by_id,
    update_company_track,
    toggle_active,
)
from utils import extract_text_from_pdf

st.set_page_config(page_title="Company Tracker", layout="wide")

st.title("🏢 Company Application Tracker")
st.markdown("Manage all your tracked job applications — update status, upload new resumes, and review AI feedback.")

# ── Helpers ──────────────────────────────────────────────────────────────────
def parse_ai(ai_str):
    if not ai_str:
        return {}
    try:
        return json.loads(ai_str) if isinstance(ai_str, str) else ai_str
    except Exception:
        return {}


def score_badge(score):
    if score is None:
        return "—"
    if score < 50:
        return f"🔴 {score}/100"
    if score < 75:
        return f"🟡 {score}/100"
    return f"🟢 {score}/100"


STATUS_OPTIONS = [
    "Analyzed",
    "Applied",
    "Phone Screen",
    "Interview Scheduled",
    "Interview Done",
    "Offer Received",
    "Accepted",
    "Rejected",
    "Withdrawn",
]

# ── Fetch data ────────────────────────────────────────────────────────────────
records = get_all_company_tracks()

if not records:
    st.info("No company applications tracked yet. Head over to the **Resume ATS Analyzer** to get started!")
    st.stop()

# ── Summary table ─────────────────────────────────────────────────────────────
st.subheader("📋 All Applications")

table_data = []
for r in records:
    ai = parse_ai(r.ai_response)
    table_data.append({
        "ID": r.id,
        "Company": r.company_name,
        "Status": r.status or "—",
        "ATS Score": score_badge(ai.get("score")),
        "Active": "✅" if r.is_active else "❌",
        "Resume": r.resume_filename or "—",
        "New Resume": r.new_resume_filename or "—",
        "Created": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "—",
    })

df = pd.DataFrame(table_data)
st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()

# ── Individual record editor ──────────────────────────────────────────────────
st.subheader("✏️ Edit / Update a Record")

record_ids = [r.id for r in records]
labels = {r.id: f"#{r.id} — {r.company_name} ({r.status or 'No status'})" for r in records}

selected_id = st.selectbox(
    "Select application to edit",
    options=record_ids,
    format_func=lambda x: labels[x],
)

record = get_company_track_by_id(selected_id)

if record:
    ai_data = parse_ai(record.ai_response)

    # ── Top info columns ────────────────────────────────────────────────────
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        st.markdown(f"**Company:** {record.company_name}")
        st.markdown(f"**Created:** {record.created_at.strftime('%Y-%m-%d %H:%M') if record.created_at else '—'}")
    with c2:
        st.markdown(f"**Original Resume:** {record.resume_filename or '—'}")
        st.markdown(f"**New Resume:** {record.new_resume_filename or '—'}")
    with c3:
        ats_score = ai_data.get("score")
        st.metric("ATS Score", score_badge(ats_score) if ats_score else "—")

    st.divider()

    # ── Editable fields ─────────────────────────────────────────────────────
    with st.form(key=f"edit_form_{selected_id}"):
        st.markdown("### 📝 Update Fields")

        col_left, col_right = st.columns(2)

        with col_left:
            new_status = st.selectbox(
                "Status",
                options=STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(record.status) if record.status in STATUS_OPTIONS else 0,
            )
            new_is_active = st.checkbox("Is Active", value=record.is_active if record.is_active is not None else True)

        with col_right:
            new_resume_file = st.file_uploader(
                "Upload New Resume (PDF)",
                type=["pdf"],
                key=f"new_resume_{selected_id}",
                help="Upload an updated version of your resume for this application.",
            )

        new_jd = st.text_area(
            "Job Description",
            value=record.jd or "",
            height=200,
            key=f"jd_{selected_id}",
        )

        submitted = st.form_submit_button("💾 Save Changes", type="primary")

        if submitted:
            updates = {
                "status": new_status,
                "is_active": new_is_active,
                "jd": new_jd,
            }

            if new_resume_file is not None:
                with st.spinner("Extracting text from new resume..."):
                    new_resume_text = extract_text_from_pdf(new_resume_file)
                updates["new_resume"] = new_resume_text
                updates["new_resume_filename"] = new_resume_file.name

            success = update_company_track(selected_id, **updates)
            if success:
                st.success("✅ Record updated successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to update record.")

    st.divider()

    # ── AI Response viewer ──────────────────────────────────────────────────
    if ai_data:
        with st.expander("🧠 View AI Analysis", expanded=False):
            if "score" in ai_data:
                score = ai_data["score"]
                if score < 50:
                    st.error(f"📊 ATS Match Score: {score}/100")
                elif score < 75:
                    st.warning(f"📊 ATS Match Score: {score}/100")
                else:
                    st.success(f"📊 ATS Match Score: {score}/100")

            for key, value in ai_data.items():
                if key == "score":
                    continue
                title = key.replace("_", " ").title()
                st.subheader(f"📌 {title}")
                if isinstance(value, list):
                    if key == "rewrites":
                        for i, item in enumerate(value):
                            with st.expander(f"Rewrite Suggestion {i+1}"):
                                st.markdown("**Original**")
                                st.code(item.get("original", ""))
                                st.markdown("**Improved**")
                                st.success(item.get("replacement", ""))
                    elif key == "missing_keywords":
                        cols = st.columns(4)
                        for i, kw in enumerate(value):
                            cols[i % 4].markdown(
                                f'<div style="padding:6px;border-radius:6px;text-align:center;font-weight:600">{kw}</div>',
                                unsafe_allow_html=True,
                            )
                    else:
                        for item in value:
                            st.markdown(f"- {item}")
                elif isinstance(value, str):
                    st.write(value)
                elif isinstance(value, dict):
                    st.json(value)

    # ── Resume text viewer ──────────────────────────────────────────────────
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if record.resume:
            with st.expander("📄 View Original Resume Text"):
                st.text(record.resume[:3000] + ("..." if len(record.resume) > 3000 else ""))

    with col_r2:
        if record.new_resume:
            with st.expander("📄 View New Resume Text"):
                st.text(record.new_resume[:3000] + ("..." if len(record.new_resume) > 3000 else ""))

    st.divider()

    # ── Danger zone ─────────────────────────────────────────────────────────
    with st.expander("⚠️ Danger Zone", expanded=False):
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🚫 Mark Inactive", key=f"deactivate_{selected_id}"):
                toggle_active(selected_id, False)
                st.warning("Marked as inactive.")
                st.rerun()
        with col_b:
            if st.button("✅ Mark Active", key=f"activate_{selected_id}"):
                toggle_active(selected_id, True)
                st.success("Marked as active.")
                st.rerun()