# OpportunityAgent

> AI-powered agent that continuously discovers, ranks, and tracks research and engineering opportunities based on your CV.

OpportunityAgent is an open-source autonomous job discovery system that searches universities, research institutes, and industry career portals to find opportunities matching a user's profile.

Instead of manually browsing dozens of websites every week, users simply upload their CV, specify their interests, and let the agent perform the search automatically.

The agent extracts skills and experience from the CV, searches hundreds of career pages, evaluates the relevance of each opportunity using LLMs, generates a ranked spreadsheet, and emails the results on a schedule.

---

## Features

- 📄 Parse PDF CVs automatically
- 🧠 Extract skills, education, publications, and experience using AI
- 🔍 Search multiple academic and industry job portals
- 🎯 Match opportunities against the user's profile
- 📊 Rank jobs using AI-generated match scores
- 📅 Sort by application deadline
- 📑 Generate Excel reports
- 📧 Email weekly reports automatically
- 🔁 Scheduled execution using GitHub Actions
- 💾 Track previously discovered opportunities
- 🚫 Remove duplicate listings

---

## Supported Opportunities

### Academia

- PhD
- Postdoctoral Fellow
- Research Assistant
- Research Engineer
- Faculty Positions
- Visiting Researcher
- Fellowships

### Industry

- Machine Learning Engineer
- AI Research Engineer
- Research Scientist
- Software Engineer
- Computer Vision Engineer
- NLP Engineer
- Robotics Engineer

---

# How it Works

```text
                    User Configuration
                           │
          ┌────────────────┴────────────────┐
          │                                 │
      Upload CV                    Enter Keywords
          │                                 │
          └────────────────┬────────────────┘
                           │
                     CV Parsing Agent
                           │
                 Skill Extraction Agent
                           │
                  Keyword Expansion Agent
                           │
                  Opportunity Search Agent
                           │
                 Duplicate Removal Agent
                           │
                   AI Matching Agent
                           │
              Deadline Prioritization Agent
                           │
                 Excel Report Generator
                           │
                     Email Notification
```

---

# Example Workflow

1. Upload CV

```
cv.pdf
```

2. Configure profile

```yaml
email: user@example.com

keywords:
  - Quantum Computing
  - Machine Learning

countries:
  - Germany
  - Switzerland
  - Spain

job_types:
  - PhD
  - Research Engineer

schedule:
  - Wednesday
  - Saturday
```

3. Run

```
python run.py
```

The agent will

- Parse the CV
- Understand your background
- Search supported sources
- Rank opportunities
- Generate an Excel report
- Email the report

---

# Example Output

| Deadline | Match | Position | Organization | Country | Salary | Link |
|-----------|--------|----------|--------------|----------|---------|------|
| Aug 3 | 95% | PhD | ETH Zurich | Switzerland | CHF 55k | ✓ |
| Aug 6 | 91% | Research Engineer | Bosch Research | Germany | €72k | ✓ |

---

# Architecture

```
OpportunityAgent

├── CV Parser
├── Skill Extractor
├── Keyword Expander
├── Search Engine
├── Opportunity Parser
├── Duplicate Detector
├── AI Matcher
├── Report Generator
├── Email Agent
└── Scheduler
```

---

# Tech Stack

| Component | Technology |
|------------|------------|
| Language | Python |
| AI | Gemini / OpenRouter |
| Parsing | PyMuPDF |
| Search | BeautifulSoup + Playwright |
| Data | SQLite |
| Reports | openpyxl |
| Email | SMTP |
| Scheduler | GitHub Actions |
| Configuration | YAML |

---

# Roadmap

## Version 1

- CV parsing
- Skill extraction
- Search multiple sources
- Excel generation
- Email reports

---

## Version 2

- AI match scoring
- Duplicate detection
- Opportunity history
- Better ranking

---

## Version 3

- Cover letter generation
- Statement of Purpose generation
- Research statement generation

---

## Version 4

- Multi-agent architecture
- User dashboard
- Resume optimization
- Application tracker
- Interview reminders

---

# Contributing

Contributions are welcome.

Feel free to add new job sources, improve ranking algorithms, or extend the AI agents.
