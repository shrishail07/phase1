
import modal
import os
import traceback
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Define Modal container image with required packages
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "fastapi[standard]",
    "pandas",
    "openpyxl",
    "pydantic",
    "langchain",
    "langchain-core",
    "langchain-groq"
)

app = modal.App("grow-with-gyan-api")

# Pydantic Schemas matching customer UI inputs and structured outputs
class StudentInput(BaseModel):
    name: str = Field(..., description="Student Full Name")
    tenth_marks: float = Field(..., ge=0, le=100)
    pu_science_marks: float = Field(..., ge=0, le=100)
    kcet_marks: int = Field(..., ge=0, le=180)
    per_year_invest: float = Field(..., ge=50000)

class CollegeRecommendation(BaseModel):
    college_name: str
    district: str
    gov_seat: int
    private_seat: int
    departments: str
    seat_type_recommended: str
    fee_pay: float
    cutoff_rank: int
    composite_rank_score: float

class AdvisoryResponse(BaseModel):
    student_name: str
    estimated_kcet_rank: int
    recommendations: List[CollegeRecommendation]
    ai_counselor_advice: str

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("groq-secret")]  # Requires GROQ_API_KEY configured in Modal
)
@modal.asgi_app()
def fastapi_app():
    web_app = FastAPI(
        title="Grow with Gyan - Modal Backend API",
        description="FastAPI service powered by Groq and Karnataka engineering datasets."
    )

    def load_or_generate_dataset():
        """Loads processed district college data or creates sample benchmark data."""
        os.makedirs("/tmp/data", exist_ok=True)
        csv_path = "/tmp/data/processed_colleges.csv"
        if os.path.exists(csv_path):
            return pd.read_csv(csv_path)

        # Sample data covering Bidar, Kalaburagi, Bengaluru, and Tumakuru
        sample_data = [
            {
                "district": "Kalaburagi",
                "college_name": "PDA College of Engineering, Kalaburagi",
                "total_intake": 660,
                "department": "Computer Science & Engineering",
                "dept_govt_seat": 90, "dept_pr_seat": 30, "cutoff_rank": 22000,
                "govt_fee": 96500, "mgmt_fee": 220000, "composite_rank_score": 8.5
            },
            {
                "district": "Kalaburagi",
                "college_name": "Appa Institute of Engineering and Technology",
                "total_intake": 360,
                "department": "Computer Science & Engineering",
                "dept_govt_seat": 60, "dept_pr_seat": 30, "cutoff_rank": 48000,
                "govt_fee": 96500, "mgmt_fee": 150000, "composite_rank_score": 7.2
            },
            {
                "district": "Bidar",
                "college_name": "Guru Nanak Dev Engineering College, Bidar",
                "total_intake": 480,
                "department": "Computer Science & Engineering",
                "dept_govt_seat": 75, "dept_pr_seat": 25, "cutoff_rank": 42000,
                "govt_fee": 96500, "mgmt_fee": 165000, "composite_rank_score": 7.5
            },
            {
                "district": "Bengaluru",
                "college_name": "Nitte Meenakshi Institute of Technology (NMIT)",
                "total_intake": 900,
                "department": "Computer Science & Engineering",
                "dept_govt_seat": 120, "dept_pr_seat": 60, "cutoff_rank": 9500,
                "govt_fee": 104000, "mgmt_fee": 450000, "composite_rank_score": 9.4
            },
            {
                "district": "Tumakuru",
                "college_name": "Siddaganga Institute of Technology (SIT)",
                "total_intake": 840,
                "department": "Computer Science & Engineering",
                "dept_govt_seat": 120, "dept_pr_seat": 40, "cutoff_rank": 7800,
                "govt_fee": 104000, "mgmt_fee": 400000, "composite_rank_score": 9.6
            }
        ]
        df = pd.DataFrame(sample_data)
        df.to_csv(csv_path, index=False)
        return df

    @web_app.get("/health")
    def health_check():
        return {"status": "healthy", "service": "Grow with Gyan Modal API"}

    @web_app.post("/api/v1/recommend", response_model=AdvisoryResponse)
    def recommend_colleges(student: StudentInput):
        try:
            # Feature 1: Estimate KCET Engineering Rank using 50% PUC PCM + 50% KCET Score
            pu_pct = student.pu_science_marks
            kcet_pct = (student.kcet_marks / 180.0) * 100.0
            composite_cet_score = (0.5 * pu_pct) + (0.5 * kcet_pct)

            if composite_cet_score >= 90:
                est_rank = int(1000 + (100 - composite_cet_score) * 400)
            elif composite_cet_score >= 75:
                est_rank = int(5000 + (90 - composite_cet_score) * 1800)
            elif composite_cet_score >= 60:
                est_rank = int(32000 + (75 - composite_cet_score) * 2800)
            else:
                est_rank = int(74000 + (60 - composite_cet_score) * 3500)
            est_rank = max(1, est_rank)

            # Feature 2: Filter matching colleges by budget and rank criteria
            df = load_or_generate_dataset()
            budget = student.per_year_invest
            matched_records = []

            for _, row in df.iterrows():
                # Government Quota Option Check
                if est_rank <= row["cutoff_rank"] and row["govt_fee"] <= budget:
                    matched_records.append({
                        "college_name": row["college_name"],
                        "district": row["district"],
                        "gov_seat": int(row["dept_govt_seat"]),
                        "private_seat": int(row["dept_pr_seat"]),
                        "departments": f"{row['department']} (Total Intake: {row['total_intake']})",
                        "seat_type_recommended": "KCET Govt Quota",
                        "fee_pay": float(row["govt_fee"]),
                        "cutoff_rank": int(row["cutoff_rank"]),
                        "composite_rank_score": float(row["composite_rank_score"])
                    })
                # Management Quota Option Check if within annual budget cap
                elif row["mgmt_fee"] <= budget:
                    matched_records.append({
                        "college_name": row["college_name"],
                        "district": row["district"],
                        "gov_seat": int(row["dept_govt_seat"]),
                        "private_seat": int(row["dept_pr_seat"]),
                        "departments": f"{row['department']} (Total Intake: {row['total_intake']})",
                        "seat_type_recommended": "Private / Management Quota",
                        "fee_pay": float(row["mgmt_fee"]),
                        "cutoff_rank": int(row["cutoff_rank"]),
                        "composite_rank_score": float(row["composite_rank_score"])
                    })

            # Sort by quality score (composite ranking)
            matched_records = sorted(matched_records, key=lambda x: x["composite_rank_score"], reverse=True)
            top_recs = matched_records[:6]

            # Feature 3: Groq LLM Advisory (Llama 3.3 70B via LangChain)
            groq_api_key = os.environ.get("GROQ_API_KEY")
            ai_advice = ""
            if groq_api_key:
                chat_llm = ChatGroq(
                    temperature=0.3,
                    model="openai/gpt-oss-120b",
                    groq_api_key=groq_api_key
                )
                prompt = ChatPromptTemplate.from_template(
                    "You are the Lead AI Counselor at 'Grow with Gyan', helping PUC Science graduates "
                    "from rural Karnataka (such as Bidar and Kalaburagi) avoid financial misallocation.\n\n"
                    "Student Profile:\n"
                    "- Name: {name}\n"
                    "- 10th Marks: {tenth}% | PUC Science PCM: {pu}% | KCET Score: {kcet}/180\n"
                    "- Estimated KCET Rank: ~{rank}\n"
                    "- Annual Budget Willing to Invest: ₹{budget}/year\n\n"
                    "Top Matched Colleges & Branches (Ranked by Quality & ROI):\n{colleges}\n\n"
                    "Provide an actionable, empathetic advisory report covering:\n"
                    "1. Government Quota vs Management Quota trade-offs based on their ₹{budget} budget.\n"
                    "2. Warning against settling for underperforming rural options if a higher-quality choice is accessible.\n"
                    "3. Recommended KEA option-entry strategy."
                )
                chain = prompt | chat_llm
                response = chain.invoke({
                    "name": student.name,
                    "tenth": student.tenth_marks,
                    "pu": student.pu_science_marks,
                    "kcet": student.kcet_marks,
                    "rank": est_rank,
                    "budget": student.per_year_invest,
                    "colleges": top_recs
                })
                ai_advice = response.content
            else:
                ai_advice = "Groq API key is not configured in Modal secrets."

            return AdvisoryResponse(
                student_name=student.name,
                estimated_kcet_rank=est_rank,
                recommendations=top_recs,
                ai_counselor_advice=ai_advice
            )
        except Exception as e:
            error_trace = traceback.format_exc()
            print("--- SERVER ERROR TRACEBACK ---\n", error_trace)
            raise HTTPException(status_code=500, detail=str(e))

    return web_app
