# 🔮 SortMail

> AI Intelligence Layer for Gmail & Outlook

SortMail is a web-based AI SaaS that acts as an intelligence layer on top of Gmail and Outlook. It helps professionals manage high-volume inboxes by summarizing threads, understanding attachments, converting emails into prioritized tasks, tracking follow-ups, and drafting contextual replies.

## ✨ Features

- **📧 Executive Briefings** — Summarize email threads into clear, actionable insights
- **📎 Attachment Intelligence** — Extract and summarize documents (PDF, DOCX, PPTX)
- **✅ Smart Task Generation** — Auto-convert emails into prioritized tasks
- **📝 Draft Copilot** — Generate contextual reply drafts with tone selection
- **⏳ Follow-up Tracking** — Track "waiting for reply" threads
- **📅 Calendar Suggestions** — Detect meeting times and deadlines

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python (FastAPI) |
| Frontend | Next.js 14 + Tailwind + shadcn/ui |
| Database | PostgreSQL |
| Vector DB | Chroma |
| LLM | Gemini / OpenAI |
| Auth | OAuth 2.0 (Google, Microsoft) |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 15+

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/sortmail.git
   cd sortmail
   ```

2. **Copy environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the app**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Manual Setup (Development)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
sortmail/
├── backend/
│   ├── app/              # FastAPI application
│   ├── contracts/        # Module contracts (DTOs)
│   ├── core/             # Business logic
│   │   ├── ingestion/    # Email fetching
│   │   ├── intelligence/ # AI processing
│   │   └── workflow/     # Task generation
│   └── tests/
├── frontend/
│   ├── src/app/          # Next.js pages
│   └── src/components/   # React components
├── docs/                 # Documentation
└── docker-compose.yml
```

## 📖 Documentation

- [Architecture](./architecture.md) — System design and diagrams
- [Database Schema](./database_schema.md) — ERD and SQL
- [Contracts](./contracts.md) — Module interface contracts
- [UI/UX Spec](./ui_ux_spec.md) — Wireframes and components
- [Sprint Plan](./sprint_plan.md) — Development timeline

## 🔒 Security

- OAuth 2.0 for email provider authentication
- JWT for session management
- Encrypted token storage
- No auto-send or auto-calendar booking
- User data isolation

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

Built with ❤️ by the SortMail Team
