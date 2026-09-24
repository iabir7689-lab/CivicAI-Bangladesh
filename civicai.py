from pathlib import Path
import pandas as pd
import re

COLUMNS = [
    "id","reporter","district","area","description","category","severity",
    "confidence","priority_score","status","created_at"
]

KEYWORDS = {
    "Waterlogging / Flood": ["waterlogging","flood","flooded","water","জলাবদ্ধ","বন্যা","পানি","পানিতে"],
    "Waste Management": ["waste","garbage","trash","dustbin","ময়লা","আবর্জনা","বর্জ্য"],
    "Road Damage": ["road","pothole","broken road","রাস্তা","গর্ত","ভাঙা"],
    "Street Lighting": ["light","lighting","lamp","streetlight","বাতি","আলো"],
    "Water Supply": ["drinking water","water supply","পানির সমস্যা","খাবার পানি"],
    "Public Health": ["sewage","drain","smell","mosquito","স্বাস্থ্য","ড্রেন","নর্দমা","মশা"],
    "Accessibility": ["wheelchair","disabled","accessibility","প্রতিবন্ধী","হুইলচেয়ার"],
    "Traffic / Mobility": ["traffic","jam","congestion","vehicle","যানজট","ট্রাফিক","গাড়ি"],
    "Other": []
}

HIGH_WORDS = ["severe","critical","danger","blocked","emergency","flooded","unsafe","মারাত্মক","জরুরি","বিপজ্জনক","পুরোপুরি"]
MED_WORDS = ["heavy","difficult","overflow","broken","bad","বেশি","কঠিন","উপচে","খারাপ"]

def _score_keywords(text, words):
    t = text.lower()
    return sum(1 for w in words if w.lower() in t)

def classify_report(text):
    t = text.strip()
    scores = {cat: _score_keywords(t, words) for cat, words in KEYWORDS.items()}
    category = max(scores, key=scores.get)
    if scores[category] == 0:
        category = "Other"
        confidence = 55
    else:
        confidence = min(96, 70 + scores[category] * 7)

    if _score_keywords(t, HIGH_WORDS) >= 1:
        severity = "Critical"
    elif _score_keywords(t, MED_WORDS) >= 1:
        severity = "High"
    elif category in ["Waterlogging / Flood","Public Health","Traffic / Mobility"]:
        severity = "Medium"
    else:
        severity = "Low"

    explanation = (
        f"The system matched the report to **{category}** using relevant civic terms. "
        f"Severity was estimated as **{severity}** from the wording and category. "
        "In a production system, this layer should be replaced/augmented with a validated Bangla NLP model and human verification."
    )
    return {"category": category, "severity": severity, "confidence": confidence, "explanation": explanation}

def calculate_priority(result, affected):
    base = {"Critical": 85, "High": 68, "Medium": 48, "Low": 25}[result["severity"]]
    affected_bonus = min(15, round((max(0, affected) ** 0.5) / 10))
    score = base + affected_bonus
    return min(100, int(score))

def load_reports(path):
    path = Path(path)
    if not path.exists():
        return pd.DataFrame(columns=COLUMNS)
    df = pd.read_csv(path)
    for c in COLUMNS:
        if c not in df.columns:
            df[c] = ""
    return df[COLUMNS]

def save_report(path, row):
    path = Path(path)
    df = load_reports(path)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(path, index=False)

def get_dashboard_metrics(df):
    if df.empty:
        return {"total":0,"active":0,"high":0,"resolved":0}
    return {
        "total": len(df),
        "active": int((df["status"] != "Resolved").sum()),
        "high": int((df["priority_score"].astype(float) >= 60).sum()),
        "resolved": int((df["status"] == "Resolved").sum())
    }

def get_area_summary(df):
    x = df.groupby(["district","category"]).size().reset_index(name="reports")
    return x.sort_values("reports", ascending=False)

def seed_demo_data(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    demo = [
        ["1001","Citizen","Dhaka","Mirpur 10","Heavy rainfall has caused severe waterlogging and vehicles are blocked.","Waterlogging / Flood","Critical",92,100,"Reported","2026-09-25 00:10:00"],
        ["1002","Citizen","Chattogram","Agrabad","Garbage is overflowing beside the market.","Waste Management","High",91,74,"In Progress","2026-09-25 00:08:00"],
        ["1003","Citizen","Rajshahi","City Center","A large pothole is damaging vehicles.","Road Damage","High",84,69,"Reported","2026-09-25 00:05:00"],
        ["1004","Citizen","Sylhet","Zindabazar","Street light is not working at night.","Street Lighting","Low",88,31,"Resolved","2026-09-24 23:55:00"],
        ["1005","Citizen","Dhaka","Uttara","Traffic congestion is causing long delays.","Traffic / Mobility","Medium",90,51,"Reported","2026-09-24 23:40:00"],
        ["1006","Citizen","Khulna","Sonadanga","Drain overflow creates an unsafe public health condition.","Public Health","High",90,72,"Reported","2026-09-24 23:20:00"],
    ]
    pd.DataFrame(demo, columns=COLUMNS).to_csv(path, index=False)
