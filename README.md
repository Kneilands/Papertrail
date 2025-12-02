<<<<<<< HEAD
# PaperTrail - Compliance Dashboard (v2.0)

A professional-grade mock compliance dashboard for small businesses. Features document tracking, renewal alerts, and an AI assistant for document analysis.

## Features
- **Modern SaaS UI:** Built with Tailwind CSS (Enterprise Slate/Navy theme).
- **Database Backed:** Uses SQLite/SQLAlchemy for real persistence (CRUD).
- **AI Integration:** - Local Text Extraction (PDFs).
  - Summarization via Hugging Face Inference API.
  - Regex-based key date detection.
- **Dashboard Stats:** Real-time calculation of compliance scores and expiration alerts.

## Setup Instructions

1. **Environment Setup**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
=======
# Papertrail
AI-powered compliance.

### **Overview**

Papertrail is an AI-powered compliance helper built for small businesses that need to stay on top of their forms, renewals, licenses, and other operational paperwork. This could be things like OSHA forms, liquor licenses, pool licenses, etc. The goal is to make compliance easy and automatic, so that business owners don’t miss important deadlines or renewal dates, and can quickly identify the necessary forms or permits to get started.

Papertrail also will act as a simple information hub, helping users learn what regulations apply to them and how to streamline their administrative processes. Over time, I plan to expand it with features like automated reminders, document uploads, and personalized AI guidance based on industry type and location.

### **Required APIs, Models, Accounts, and Platforms**
*AI / Models*
```
OpenAI API
This is going to be used to power the AI assistant.

Model: GPT-4o (or GPT-4 Turbo for lower cost)

Account: OpenAI Developer Account

Environment Variable: OPENAI_API_KEY
```
*Data and Compliance Sources*
```
U.S. Small Business Administration (SBA) API
  Website: https://www.sba.gov/developer
  This will provide data on business setup steps, permits, and regulations by state and industry.

Secretary of State API / portal
  Illinois Business Portal
  This will be used to verify licenses, filing requirements, and renewal dates.
```
*Notification / Reminder Service*
```
SendGrid API
Sends automated email reminders for upcoming expirations or required filings.

Account: https://sendgrid.com

Environment Variable: SENDGRID_API_KEY
```
*Platforms*
```
- Language: Python 3.12
- Framework: FastAPI
- Frontend: HTML, JavaScript
- Database: SQLite
- Version Control: GitHub
```
>>>>>>> origin/main
