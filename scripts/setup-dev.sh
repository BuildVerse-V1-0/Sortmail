#!/bin/bash
# Setup Development Environment

set -e

echo "🚀 Setting up SortMail development environment..."

# Backend setup
echo "📦 Setting up backend..."
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cd ..

# Frontend setup
echo "📦 Setting up frontend..."
cd frontend
npm install
cd ..

# Copy env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Created .env file - please fill in your API keys"
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys"
echo "2. Run: docker-compose up -d"
echo "3. Run: make dev"
