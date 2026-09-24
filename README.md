# 🇧🇩 CivicAI Bangladesh

AI-powered civic problem reporting, prioritization and response intelligence.

## 1. What it does

CivicAI converts citizen reports into structured civic intelligence:

**Report → Understand → Prioritize → Respond → Resolve**

The prototype supports:
- Civic complaint submission
- Bangla/English keyword-based categorization
- Severity estimation
- Priority scoring
- National-style dashboard
- District/category analytics
- CSV export
- Fully local demo mode with no API key

## 2. Project structure

```text
CivicAI_Bangladesh/
├── app.py
├── civicai.py
├── requirements.txt
├── README.md
├── .gitignore
└── data/
    └── reports.csv
```

## 3. Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 4. Deploy on Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload `app.py`, `civicai.py`, `requirements.txt`, `.gitignore`, `README.md`, and the `data` folder.
3. Open Streamlit Community Cloud.
4. Select the GitHub repository.
5. Set main file to `app.py`.
6. Deploy.

No secret/API key is required for this demo.

## 5. Demo flow

1. Open **National Dashboard**.
2. Show the priority queue.
3. Go to **Report a Problem**.
4. Submit:
   `Heavy rainfall has flooded the road and blocked vehicles near the market.`
5. Show AI category, severity and priority.
6. Return to dashboard and show the new incident.
7. Open **Insights** and show district/category analytics.

## 6. Production roadmap

The competition prototype deliberately avoids external APIs so it remains easy to deploy and demo. For a real national system, add:

- PostgreSQL/Supabase
- Auth + role-based access
- GPS and photo evidence
- Bangla transformer NLP
- Computer vision model
- Duplicate incident clustering
- Real weather/IoT feeds
- Human verification workflow
- Audit logs
- Encryption and privacy controls
- Rate limiting and abuse prevention
- Government/NGO API integration

## 7. Important claim

No software can honestly be guaranteed to be “100% bug-free” before real-world testing. This repository is designed to be a clean, dependency-light competition prototype. Production deployment requires testing, monitoring, security review and validation with real users/data.
