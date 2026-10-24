import streamlit as st
import pandas as pd
import requests

# Retrieve Modal deployment URL safely from Streamlit Cloud Secrets
MODAL_API_URL = st.secrets.get(
    "MODAL_API_URL", 
    "https://your-modal-username--grow-with-gyan-api-fastapi-app.modal.run/api/v1/recommend"
)

st.set_page_config(
    page_title="Grow with Gyan | VTU & KCET AI Advisor",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Grow with Gyan: Smart VTU & KCET College Advisor")
st.markdown("**Bridging information deficits for rural Karnataka PUC Science graduates with transparent ROI and cutoff data.**")

with st.sidebar:
    st.header("📋 Student Academic Profile")
    with st.form("student_form"):
        name = st.text_input("Student Full Name", value="Basavaraj Patil")
        tenth_marks = st.number_input("10th Std Marks (%)", min_value=35.0, max_value=100.0, value=85.0, step=0.5)
        pu_science_marks = st.number_input("PUC II Science (PCM %)", min_value=35.0, max_value=100.0, value=82.0, step=0.5)
        kcet_marks = st.number_input("KCET Marks (Out of 180)", min_value=1, max_value=180, value=88, step=1)
        per_year_invest = st.number_input("Max Annual Budget (₹ / Year)", min_value=50000, max_value=600000, value=200000, step=10000)
        submitted = st.form_submit_button("🔍 Find Best ROI Colleges")

if submitted:
    with st.spinner("Analyzing rank on Modal and running Groq Llama 3.3 AI advisory..."):
        payload = {
            "name": name,
            "tenth_marks": tenth_marks,
            "pu_science_marks": pu_science_marks,
            "kcet_marks": kcet_marks,
            "per_year_invest": per_year_invest
        }
        try:
            response = requests.post(MODAL_API_URL, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()

            # Top Metrics Dashboard
            col1, col2, col3 = st.columns(3)
            col1.metric("Student Name", data["student_name"])
            col2.metric("Estimated KCET Rank", f"#{data['estimated_kcet_rank']:,}")
            col3.metric("Annual Budget Cap", f"₹{per_year_invest:,.0f}/yr")

            st.subheader("🏛️ Optimal College Seat & Fee Matrix")
            recs = data["recommendations"]
            if recs:
                df_res = pd.DataFrame(recs)
                display_df = df_res[[
                    "college_name",
                    "district",
                    "gov_seat",
                    "private_seat",
                    "departments",
                    "seat_type_recommended",
                    "fee_pay",
                    "composite_rank_score"
                ]].rename(columns={
                    "college_name": "College Name",
                    "district": "District",
                    "gov_seat": "Govt Seats",
                    "private_seat": "Private Seats",
                    "departments": "Department & Intake",
                    "seat_type_recommended": "Recommended Quota",
                    "fee_pay": "Fee to Pay (₹/yr)",
                    "composite_rank_score": "Gyan Quality Score"
                })
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.warning("No matching colleges found within this budget and rank combination.")

            st.subheader("🤖 Groq Llama 3.3 AI Counselor Report")
            st.info(data["ai_counselor_advice"])

        except Exception as e:
            st.error(f"Failed to connect to Modal backend API: {e}")
else:
    st.info("👈 Enter your academic details and annual investment budget in the sidebar to generate your tailored counseling roadmap.")
