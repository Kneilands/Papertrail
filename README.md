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