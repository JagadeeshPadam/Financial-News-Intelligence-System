#!/bin/bash

# AI-Powered Financial News Intelligence System - Setup Script

echo "🚀 Financial News Intelligence System - Setup"
echo "=============================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
cd BE
python3 -m venv venv

# Activate virtual environment
echo "   Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model
echo ""
echo "🔽 Downloading spaCy language model..."
python -m spacy download en_core_web_sm

# Create .env file if not exists
echo ""
echo "⚙️  Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "   ✅ Created .env file from template"
    echo "   ⚠️  IMPORTANT: Please add your OpenAI API key to BE/.env"
else
    echo "   ℹ️  .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Add your OpenAI API key to BE/.env"
echo "2. Activate the virtual environment: cd BE && source venv/bin/activate"
echo "3. Load mock data: python load_data.py"
echo "4. Start the backend: uvicorn api.main:app --reload"
echo "5. Open FE/index.html in your browser"
echo ""
