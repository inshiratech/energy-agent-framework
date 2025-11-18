# energy-agent-framework
# Multi-Agent Energy Analysis Framework

Three specialized AI agents that analyze energy bills, research industry benchmarks, and generate actionable reports.

## Agents

1. **Bill Analyzer** - Extracts costs, usage, and rates from PDF bills
2. **Web Researcher** - Finds industry benchmarks using web search
3. **Report Generator** - Compiles findings into actionable insights

## Deploy to Streamlit Cloud

1. Fork or clone this repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repository
5. Set main file: `app.py`
6. Add your Anthropic API key in Secrets:
```
   ANTHROPIC_API_KEY = "sk-ant-..."
```
7. Click Deploy!

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

Add `.streamlit/secrets.toml`:
```toml
ANTHROPIC_API_KEY = "your-key-here"
```

## How It Works

1. Upload a PDF energy bill
2. Agent #1 extracts data from the PDF
3. Agent #2 searches the web for industry benchmarks
4. Agent #3 generates a comprehensive report
5. View results in expandable sections

## Tech Stack

- **Streamlit** - Web framework
- **Claude API** - AI agents (Sonnet 4)
- **Anthropic SDK** - API integration
```

---

**Step 3: Deploy to Streamlit Cloud**

1. Go to https://share.streamlit.io
2. Click "New app"
3. Sign in with GitHub
4. Select your repository: `energy-agent-framework`
5. Main file path: `app.py`
6. Click "Advanced settings" → "Secrets"
7. Add:
```
   ANTHROPIC_API_KEY = "your-actual-anthropic-api-key"
