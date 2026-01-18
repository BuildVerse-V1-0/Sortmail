# Contributing to SortMail

Thank you for contributing to SortMail! Please follow these guidelines.

## Development Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your API keys
3. Run `docker-compose up -d` to start services
4. Run `make setup` to install dependencies

## Git Workflow

### Branches
- `main` — Production-ready code only
- `dev` — Integration branch
- `feature/*` — Individual features

### Pull Request Process
1. Create a feature branch from `dev`
2. Make your changes
3. Ensure tests pass: `make test`
4. Ensure lint passes: `make lint`
5. Open a PR to `dev`
6. Get 1 approval
7. Merge

## Code Style

### Backend (Python)
- Follow PEP 8
- Use Ruff for linting
- Type hints required
- Docstrings for public functions

### Frontend (TypeScript)
- Follow ESLint rules
- Use Prettier for formatting
- TypeScript strict mode

## Contract Rules

See [contracts.md](./contracts.md) for full details.

1. **Only import from `backend/contracts/`**
2. **Never pass raw dicts or ORM objects**
3. **Add new optional fields only**
4. **Contract changes require Platform Lead approval**

## Testing

- Backend: `cd backend && pytest`
- Frontend: `cd frontend && npm test`
- All tests must pass before merge

## Questions?

Open an issue or ask in the team Slack.
