# 🛡️ Mini QMS – Student Software Project Risk Management

A Mini Quality Management System (QMS) designed to help student software development teams identify, assess, monitor, and manage project risks. The application provides a centralized dashboard for risk tracking, mitigation planning, and quality reporting.

## 📌 Project Overview

Student software projects may face risks such as missed deadlines, incomplete requirements, database failures, coding errors, and resource shortages. Managing these risks systematically helps improve project quality and delivery.

Mini QMS provides a simple web-based solution to register risks, calculate risk scores, assign responsibilities, track mitigation actions, and generate reports.

## 🎯 Objectives

- Identify and document software project risks.
- Assess risks using probability and impact.
- Automatically calculate risk scores and priority levels.
- Assign risk owners and mitigation actions.
- Monitor risk status and overdue activities.
- Generate risk summaries and downloadable reports.

## ✨ Features

- **Dashboard:** Displays project risk statistics and visualizations.
- **Project Management:** Create and manage student software projects.
- **Risk Register:** Add, view, edit, and delete project risks.
- **Risk Assessment:** Automatically calculates risk scores.
- **Mitigation Tracking:** Manage risk owners, action plans, deadlines, and statuses.
- **Risk History:** Records risk registration and status changes.
- **Quality Reports:** Displays risk score distributions and closure metrics.
- **CSV Export:** Download risk registers and risk history for analysis.

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Web Framework | Streamlit |
| Database | SQLite |
| Data Processing | Pandas |
| Data Visualization | Plotly |
| Version Control | Git and GitHub |

## 📊 Risk Assessment Methodology

The system uses the following formula:

**Risk Score = Probability × Impact**

Both probability and impact are measured on a scale of 1 to 5.

| Risk Score | Risk Level | Recommended Action |
|---:|---|---|
| 1–4 | Low | Accept and monitor |
| 5–9 | Medium | Plan preventive actions |
| 10–16 | High | Prioritize mitigation |
| 17–25 | Critical | Take immediate action |

## 📁 Project Structure

```text
Mini-QMS/
├── app.py
├── database.py
├── risk_engine.py
├── requirements.txt
├── .gitignore
├── .gitattributes
└── README.md
```

The `qms.db` SQLite database is created automatically when the application initializes.

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.10 or later
- Git
- Visual Studio Code (recommended)

### 1. Clone the repository

```bash
git clone https://github.com/Nitish-jm25/Mini-QMS.git
cd Mini-QMS
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```cmd
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
streamlit run app.py
```

Open the following URL in your browser:

`http://localhost:8501`

## 🚀 How to Use

1. Open the application in your browser.
2. Navigate to the **Projects** tab and create a project.
3. Open **Risk Register** and add risks with probability, impact, and ownership details.
4. Review automatically calculated risk scores and priority levels.
5. Use **Mitigation** to update action plans and risk statuses.
6. Monitor project statistics and visualizations in the dashboard.
7. Open **Reports** to view quality metrics and download CSV reports.

## 🧪 Example Risk

| Attribute | Example |
|---|---|
| Risk | Project deadline may be missed |
| Probability | 4 |
| Impact | 5 |
| Risk Score | 20 |
| Risk Level | Critical |
| Mitigation | Define weekly milestones and monitor progress |
| Status | Open |

## 🔮 Future Enhancements

- Risk heatmap visualization.
- PDF quality report generation.
- User authentication and role-based access.
- Automated notifications for overdue risks.
- Enhanced audit history and quality metrics.

## 🎓 Project Information

**Project Title:** Mini QMS for Student Software Project Risk Management

**Domain:** Software Engineering and Total Quality Management (TQM)

**Project Type:** Academic Mini Project

## 👨‍💻 Author

**Nitish Raj**

GitHub: [Nitish-jm25](https://github.com/Nitish-jm25)

## 📄 License

This project is developed for academic and educational purposes.
