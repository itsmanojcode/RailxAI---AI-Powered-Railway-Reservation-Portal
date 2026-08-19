# 🚆 RailxAI Express - AI Reservation Portal

A modern, glassmorphic Railway Reservation Web Application built using Python, Streamlit, SQLite, and Google Gemini AI.

## Key Features
- **Modern Dark Glassmorphic UI:** Built with clean custom CSS accents and responsive metrics.
- **Automated API Key Management:** Loads `GEMINI_API_KEY` directly from `.env`.
- **Instant PDF Ticket Generation:** Built with ReportLab for structured E-Tickets.
- **Real-Time PNR Tracker:** Queries local SQLite database for real-time status.
- **Gemini AI Travel Assistant:** Powered by `google-genai` SDK (`gemini-2.5-flash`).

## How to Run locally

1. Open folder in VS Code.
2. Ensure `.env` contains your key:
   ```env
   GEMINI_API_KEY=AIzaSy...

