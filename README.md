# Finbotics - AI-Powered Financial Assistant

## Overview

Finbotics is an intelligent financial analysis assistant that helps users query and understand their company's financial data through natural language conversations. Built using CrewAI's multi-agent framework, it combines multiple specialized AI agents to provide comprehensive financial insights.

### Key Features

- **Natural Language Queries**: Ask questions about expenses, revenue, cash flow, and vendors in plain English
- **Multi-Source Analysis**: Combines data from CSV files (general ledger, P&L, balance sheet) with email context
- **Specialized Agents**: Different AI agents handle specific domains like expense analysis, cash flow calculations, and email research
- **Secure Access**: Built-in security validation ensures data isolation between customers
- **Comprehensive Reports**: Generates professional reports with source citations for trust and verification
- **Multi-Model Support**: Works with OpenAI and Google Gemini LLM providers

### Example Queries

- "How much did I spend on OpenAI in February?"
- "What's my current runway?"
- "What caused the spike in Licenses and Fees in January?"
- "What ended up happening with the Sevenn invoices?"
- "What are my biggest recurring expenses?"

## Architecture

The system uses specialized agents:
- **Query Router**: Analyzes queries and routes to appropriate specialists
- **Expense Analyst**: Handles spending analysis and vendor expenses
- **Cash Flow Analyst**: Calculates burn rate and runway
- **Email Context Agent**: Searches correspondence for additional context
- **Report Generator**: Creates formatted, professional reports
- **Security Guardian**: Validates access permissions

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- API key for your chosen LLM provider (OpenAI or Google Gemini)

### Setup Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd finbotics
```

2. **Create a virtual environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Create .env file from example
cp .env.example .env

# Edit .env and configure your LLM provider
```

Example `.env` configuration:

```env
# Model Configuration
MODEL=gemini/gemini-pro  # or gpt-4, gpt-3.5-turbo, etc.

# API Keys (configure based on your chosen model)
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # if using OpenAI models
```

### Supported Models

- **Google Gemini**: `gemini/gemini-pro`
- **OpenAI**: `gpt-4`, `gpt-3.5-turbo`

5. **Prepare your data**
```bash
# Create data directories
mkdir -p data/csv data/emails

# Place your CSV files in data/csv/:
# - general_ledger.csv
# - balance_sheet.csv
# - profit_loss.csv
# - expense_summary.csv

# Place email text files in data/emails/:
# - email_jan.txt
# - email_feb.txt
# etc.
```

## Project Structure

```
finbotics/
├── src/finbotics/
│   ├── config/
│   │   ├── agents.yaml     # Agent configurations
│   │   └── tasks.yaml      # Task definitions
│   ├── tools/              # Custom tools
│   │   ├── financial_formatter.py
│   │   ├── email_search_tool.py
│   │   └── security_tool.py
│   ├── crew.py            # Main crew orchestration
│   └── orchestrator.py    # Query routing logic
├── data/
│   ├── csv/              # Financial data files
│   └── emails/           # Email correspondence
├── tests/                # Test scripts
├── .env                  # Environment variables (create from .env.example)
├── .env.example          # Example environment configuration
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Running Tests

### 1. Query Classification Test
Tests the basic query classifier agent:
```bash
python test_classifier.py
```

### 2. Expense Analysis Test
Tests expense tracking and analysis:
```bash
python test_expense_analyst.py
```

### 3. End-to-End Flow Test
Tests complete workflow from query to report:
```bash
python test_end_to_end.py
```

### 4. Advanced Agents Test
Tests runway calculations and email search:
```bash
python test_advanced_agents.py
```

### 5. Routing Test
Tests sophisticated query routing:
```bash
python test_routing.py
```

## Data Format Requirements

### CSV Files

**general_ledger.csv**
```
Date,Account,Description,Vendor,Amount,Category
2024-02-01,Software,API Usage,OpenAI,1200.00,Technology
2024-02-05,Insurance,Health Premium,BlueCross,500.00,Benefits
```

**balance_sheet.csv**
- Standard balance sheet with Assets, Liabilities, Equity sections
- Used for cash position and runway calculations

**profit_loss.csv**
- Monthly revenue and expense breakdowns
- Used for trend analysis and burn rate calculations

### Email Files

Plain text files in `data/emails/`:
```
Subject: Invoice Issue - Sevenn
Date: 2024-02-15

Hi team,

We're having issues with the Sevenn invoice for January...
```

## Troubleshooting

### Common Issues

1. **API Key Errors**
   ```
   Error: Invalid API key
   ```
   - Check `.env` file has correct API key
   - Ensure MODEL matches your API provider
   - No spaces around the = sign in .env

2. **Module Not Found**
   ```
   ModuleNotFoundError: No module named 'crewai'
   ```
   - Activate virtual environment: `source venv/bin/activate`
   - Install dependencies: `pip install -r requirements.txt`

3. **File Not Found**
   ```
   FileNotFoundError: data/csv/general_ledger.csv
   ```
   - Create data directories: `mkdir -p data/csv data/emails`
   - Ensure CSV files have correct names and extensions

4. **Agent Configuration Errors**
   - Check YAML indentation in config files
   - Ensure all required fields are present

## Quick Start Example

```python
from src.finbotics.crew import Finbotics
from crewai import Crew, Task

# Initialize the system
finbotics = Finbotics()

# Create a simple query task
task = Task(
    description="How much did I spend on software in February?",
    expected_output="Total software spending for February",
    agent=finbotics.expense_analyst()
)

# Create and run crew
crew = Crew(
    agents=[finbotics.expense_analyst()],
    tasks=[task],
    process="sequential"
)

result = crew.kickoff()
print(result)
```

## Security Considerations

- Customer data isolation enforced through Security Guardian
- All data access is logged for audit purposes
- Keep API keys secure and never commit to version control
- Use environment variables for sensitive configuration

## Dependencies

Core dependencies (from requirements.txt):
- `crewai[tools]>=0.11.0` - Multi-agent framework
- `google-generativeai>=0.3.0` - Google Gemini support
- `openai>=1.0.0` - OpenAI GPT support
- `pandas>=2.0.0` - Data processing
- `pyyaml>=6.0` - Configuration files
- `python-dotenv>=1.0.0` - Environment variables

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[Your License Here]

## Support

For issues and questions:
- Check the Troubleshooting section above
- Review test files for usage examples
- Open an issue on GitHub

---

**Note**: This is a proof-of-concept implementation. For production use, additional security measures, error handling, and performance optimizations may be required.