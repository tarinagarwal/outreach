# Contributing to Outreach Automation

Thank you for your interest in contributing to Outreach Automation!

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/AIkaptan/outreach.git
cd outreach

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp env.example .env
# Edit .env with your credentials

# Run the application
python app.py
```

## Environment Setup

You'll need:

- OpenAI API key
- Google Cloud credentials (for Sheets and Docs API)
- SMTP credentials for email sending

## Code Style

- Follow PEP 8 guidelines
- Add docstrings to functions and classes
- Write meaningful commit messages
- Keep services modular and testable

## Reporting Issues

Please use the GitHub issue tracker to report bugs or suggest features.
