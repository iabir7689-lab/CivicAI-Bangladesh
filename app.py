import streamlit as st
from pathlib import Path
from datetime import datetime
import pandas as pd

from civicai import (
    load_reports, save_report, classify_report, calculate_priority,
    get_dashboard_metrics, get_area_summary, seed_demo_data
)

st.set_page_config(
    page_title="CivicAI Bangladesh",
    page_icon="🇧🇩",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
.hero {
    padding: 1.4rem 1.5rem; border-radius: 18px;
    background: linear-gradient(135deg,#063b2a,#0b6b4a);
    color: white; margin-bottom: 1rem;
}
.hero h1 {margin:0 0 .25rem 0; font-size:2.2rem;}
.hero p {margin:.15rem 0; opacity:.92;}
.badge {padding:.2rem .55rem; border-radius:999px; font-weight:700;}
</style>
""", unsafe_allow_html=True)

DATA = Path("data/reports.csv")
if not DATA.exists():
    seed_demo_data(DATA)

st.markdown("""
<div class="hero">
<h1>🇧🇩 CivicAI Bangladesh</h1>
<p>AI-powered civic problem reporting, prioritization and response intelligence.</p>
<p><b>Report → Understand → Prioritize → Respond → Resolve</b></p>
</div>
""", unsafe_allow_html=True)

reports = load_reports(DATA)
metrics = get_dashboard_metrics(reports)

# ---------- Sidebar ----------
with st.sidebar:
    st.header("CivicAI Control")
    page = st.radio(
        "Navigate",
        ["🏠 National Dashboard", "📣 Report a Problem", "🧠 AI Analysis", "📊 Insights", "ℹ️ About"]
    )
    st.divider()
    st.caption("Demo mode: local CSV storage. No API key required.")
    if st.button("🔄 Reload data", use_container_width=True):
        st.rerun()

# ---------- Dashboard ----------
if page == "🏠 National Dashboard":
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Reports", metrics["total"])
    c2.metric("Active Problems", metrics["active"])
    c3.metric("High/Critical", metrics["high"])
    c4.metric("Resolved", metrics["resolved"])

    st.subheader("🚨 Priority Queue")
    if reports.empty:
        st.info("No reports yet.")
    else:
        q = reports[reports["status"] != "Resolved"].sort_values(
            ["priority_score","created_at"], ascending=[False, False]
        ).head(12).copy()
        q["priority"] = q["priority_score"].apply(
            lambda x: "🔴 Critical" if x >= 80 else ("🟠 High" if x >= 60 else ("🟡 Medium" if x >= 35 else "🟢 Low"))
        )
        st.dataframe(
            q[["id","district","category","severity","priority_score","priority","status","created_at"]],
            use_container_width=True, hide_index=True
        )

    left,right = st.columns(2)
    with left:
        st.subheader("📍 Problems by Category")
        cat = reports["category"].value_counts() if not reports.empty else pd.Series(dtype=int)
        st.bar_chart(cat)
    with right:
        st.subheader("🗺️ District Distribution")
        dist = reports["district"].value_counts().head(12) if not reports.empty else pd.Series(dtype=int)
        st.bar_chart(dist)

    st.subheader("⚡ Live Situation")
    if not reports.empty:
        latest = reports.sort_values("created_at", ascending=False).head(6)
        for _, r in latest.iterrows():
            icon = "🔴" if r["priority_score"] >= 80 else ("🟠" if r["priority_score"] >= 60 else "🟡")
            st.write(f"{icon} **{r['district']}** — {r['category']} — priority **{r['priority_score']}/100** — {r['status']}")

# ---------- Report ----------
elif page == "📣 Report a Problem":
    st.subheader("📣 Citizen Problem Report")
    st.caption("Submit a civic issue. The local AI engine will categorize it and calculate a response priority.")

    with st.form("report_form", clear_on_submit=True):
        col1,col2 = st.columns(2)
        with col1:
            name = st.text_input("Reporter name (optional)")
            district = st.selectbox("District", [
                "Dhaka","Chattogram","Rajshahi","Khulna","Sylhet","Barishal",
                "Rangpur","Mymensingh","Cumilla","Gazipur","Narayanganj","Other"
            ])
            area = st.text_input("Area / landmark", placeholder="e.g. BAUET Gate")
        with col2:
            description = st.text_area("Describe the problem", placeholder="Example: Heavy rain has caused waterlogging and vehicles are struggling to move.")
            affected = st.number_input("Estimated people affected", min_value=1, max_value=1000000, value=50, step=10)
            st.caption("For a real deployment, GPS/photo upload can be added with privacy safeguards.")
        submitted = st.form_submit_button("🚀 Submit & Analyze", use_container_width=True)

    if submitted:
        if len(description.strip()) < 8:
            st.error("Please provide a little more detail about the problem.")
        elif not area.strip():
            st.error("Please enter an area or landmark.")
        else:
            result = classify_report(description)
            score = calculate_priority(result, affected)
            row = {
                "id": datetime.now().strftime("%Y%m%d%H%M%S%f")[-10:],
                "reporter": name.strip() or "Anonymous",
                "district": district,
                "area": area.strip(),
                "description": description.strip(),
                "category": result["category"],
                "severity": result["severity"],
                "confidence": result["confidence"],
                "priority_score": score,
                "status": "Reported",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            save_report(DATA, row)
            st.success("Report received successfully.")
            a,b,c = st.columns(3)
            a.metric("AI Category", result["category"])
            b.metric("Severity", result["severity"])
            c.metric("Priority", f"{score}/100")
            st.info(result["explanation"])

# ---------- AI Analysis ----------
elif page == "🧠 AI Analysis":
    st.subheader("🧠 Explainable AI Analysis")
    st.write("This prototype uses a transparent, offline classification engine. It is intentionally deterministic for a reliable demo.")
    text = st.text_area("Paste a civic complaint", "Heavy rainfall has flooded the road and blocked vehicles near the market.")
    affected = st.number_input("Affected people", 1, 1000000, 500, 50)
    if st.button("Analyze", type="primary"):
        result = classify_report(text)
        score = calculate_priority(result, affected)
        st.markdown(f"### {result['category']}")
        st.write(result["explanation"])
        c1,c2,c3 = st.columns(3)
        c1.metric("Severity", result["severity"])
        c2.metric("Confidence", f"{result['confidence']}%")
        c3.metric("Priority", f"{score}/100")
        st.progress(score / 100)
        st.caption("Priority is a decision-support indicator, not an automatic government decision.")

# ---------- Insights ----------
elif page == "📊 Insights":
    st.subheader("📊 Civic Intelligence")
    if reports.empty:
        st.info("No data available.")
    else:
        area = get_area_summary(reports)
        st.dataframe(area, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Download civic report CSV",
            reports.to_csv(index=False).encode("utf-8"),
            file_name="civicai_reports.csv",
            mime="text/csv"
        )
        st.subheader("Category Trend")
        st.line_chart(
            reports.assign(date=pd.to_datetime(reports["created_at"]).dt.date)
            .groupby(["date","category"]).size().unstack(fill_value=0)
        )

# ---------- About ----------
else:
    st.subheader("ℹ️ About CivicAI")
    st.markdown("""
### Vision
Build a privacy-aware, AI-assisted civic intelligence layer that helps communities and service organizations understand local problems faster.

### Core pipeline
**Citizen report → AI categorization → severity estimation → priority score → dashboard → human response → resolution**

### Why this prototype is competition-ready
- Bangladesh-focused civic use cases
- Real-time style workflow
- Explainable AI instead of a black-box claim
- Works without paid APIs or secrets
- Streamlit + GitHub friendly
- Easy to replace demo engine with a trained ML model later

### Important deployment note
A production national platform should use authenticated APIs, a proper database, role-based access, audit logs, rate limiting, image moderation, encryption, consent, and human verification before operational decisions.
""")
