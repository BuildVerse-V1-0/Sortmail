# Contributing to SortMail

Welcome to SortMail! This guide helps you get started quickly.

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/devhubwtf/Sortmail.git
cd Sortmail

# 2. Create your branch
git checkout -b feature/your-feature-name

# 3. Set up environment
cp .env.example .env
# Edit .env with your API keys

# 4. Start services
docker-compose up -d postgres redis chroma

# 5. Start backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 6. Start frontend (new terminal)
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
sortmail/
├── backend/           # Team A, B, C work here
│   ├── core/          # Business logic
│   │   ├── auth/      # Team A: OAuth, JWT
│   │   ├── ingestion/ # Team A: Gmail/Outlook API
│   │   ├── intelligence/ # Team B: LLM, summarization
│   │   ├── workflow/  # Team C: Tasks, drafts, priority
│   │   └── storage/   # Team A: Database
│   ├── api/routes/    # API endpoints
│   ├── models/        # SQLAlchemy models
│   ├── contracts/     # Shared data types
│   └── tests/         # Tests + demo data
│
└── frontend/          # Team D works here
    └── src/
        ├── app/       # Pages
        ├── components/ # React components
        └── utils/     # API client
```

## 🔄 Workflow

### Branch Naming
```
feature/team-a-gmail-oauth
feature/team-b-summarizer
feature/team-c-priority-engine
feature/team-d-thread-list
bugfix/issue-number-description
```

### Commit Messages
```
feat(auth): implement Google OAuth flow
fix(intel): handle empty email body
docs(readme): update installation steps
```

### Pull Request Process
1. Create PR against `main`
2. Fill out the template
3. Request review from your team lead
4. Wait for CI to pass
5. Merge after approval

## 📝 Code Style

### Python (Backend)
- Use type hints
- Format with `black`
- Lint with `ruff`
- Docstrings for public functions

```python
def summarize_thread(messages: List[EmailMessage]) -> str:
    """
    Summarize an email thread in 2-3 sentences.
    
    Args:
        messages: List of email messages in the thread
        
    Returns:
        A concise summary of the thread
    """
    pass
```

### TypeScript (Frontend)
- Use strict mode
- Format with Prettier
- No `any` types
- Props interfaces for components

```tsx
interface ThreadCardProps {
  threadId: string;
  subject: string;
  summary: string;
}

export function ThreadCard({ threadId, subject, summary }: ThreadCardProps) {
  // ...
}
```

## 🧪 Testing

### Run Tests
```bash
# Backend
cd backend
pytest tests/ -v

# Frontend
cd frontend
npm test
```

### Demo Data
Use `backend/tests/demo_data.py` for testing. It has 4 realistic scenarios.

## 🤝 Communication

- **Daily Updates**: Post in #sortmail-dev Slack/Discord
- **Questions**: Ask in your team channel (#team-backend, #team-intel, etc.)
- **Blockers**: Flag immediately to Platform Lead

## 📋 Your First PR Checklist

- [ ] Code follows style guide
- [ ] Tests pass locally
- [ ] New code has tests
- [ ] Updated docs if needed
- [ ] PR description explains changes
