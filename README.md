# Finbotics - AI Financial Assistant

AI-powered financial query system that analyzes CSV data and email correspondence using natural language.

## Quick Start

### Prerequisites
- Python 3.10-3.12
- Google Gemini key

### Installation

1. **Clone and setup**
```bash
git clone <repository-url>
cd finbotics
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure API key**
```bash
cp .env.example .env
# Edit .env and add your API key:
# GEMINI_API_KEY=your_key_here
```

3. **Prepare data**
```bash
mkdir -p data/csv data/emails
# Add your CSV files to data/csv/
# Add your email files to data/emails/
```

### Run Application

```bash
python run_finbotics.py
```

Navigate to http://localhost:8501

## Required Files

**CSV files in `data/csv/`:**
- general_ledger.csv
- expense_summary.csv  
- balance_sheet.csv
- profit_loss.csv

**Email files in `data/emails/`:**
- Plain text files (e.g., email_jan.txt)

## Example Queries

- "How much did I spend on OpenAI in February?"
- "What's my current runway?"
- "What happened with the Sevenn invoices?"
- "Show me my top 5 vendors"

## Troubleshooting

- **API Key Error**: Check .env file has correct key
- **Module Not Found**: Run `pip install -r requirements.txt`
- **No Database**: Choose 'y' when prompted to initialize
