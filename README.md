# Papertrail
AI-powered compliance.

### **Overview**

Papertrail is an AI-powered compliance helper built for small businesses that need to stay on top of their forms, renewals, licenses, and other operational paperwork. The goal is to make compliance easy and automatic, so that business owners don’t miss important deadlines or renewal dates, and can quickly identify the necessary forms or permits to get started.

Papertrail also acts as a simple information hub, helping users learn what regulations apply to them and how to streamline their administrative processes. Over time, I plan to expand it with features like automated reminders, document uploads, and personalized AI guidance based on industry type and location.

### **Required APIs, Models, Accounts, and Platforms**
*AI / Models*
```
OpenAI API
Used to power the AI assistant, which helps business owners identify required licenses, forms, and renewals.

Model: GPT-4o (or GPT-4 Turbo for lower cost)

Account: OpenAI Developer Account

Environment Variable: OPENAI_API_KEY
```
*Data and Compliance Sources*
```
U.S. Small Business Administration (SBA) API
Provides data on business setup steps, permits, and regulations by state and industry.

Website: https://www.sba.gov/developer

State Secretary of State APIs / Portals
Used to verify licenses, filing requirements, and renewal dates.

Example: Illinois Business Portal
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
