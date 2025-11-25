# PathMentor – AI Learning Assistant

PathMentor is an AI-powered study assistant built using Google’s Gemini API. It helps students create personalized study plans, get explanations, run code safely, and retrieve information through intelligent agents.

## Features

- Personalized study planning
- Gemini-powered AI chat
- Built-in web search
- Persistent session history
- Simple browser-based UI

## Architecture

```
User Input
    ↓
[Orchestrator Service]
    ↓
┌─────────────────────────────────────┐
│  LLM Agent (Gemini-Powered)         │
│  • Natural language understanding   │
│  • Context-aware responses          │
│  • Gemini 2.5-flash model          │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Planning Agent                     │
│  • Decomposes learning goals        │
│  • Creates actionable steps         │
│  • Structures study paths           │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Loop Agent                         │
│  • Iterative refinement             │
│  • Quality validation               │
│  • Output optimization              │
└─────────────────────────────────────┘
    ↓
Response with Tools
    ↓
[Study Planner | Code Executor | Web Search]
    ↓
User
```

## Project Structure

```
PathMentor/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── README.md                 # Documentation
│
├── agents/                   # AI Agents
│   ├── llm_agent.py         # Gemini-powered LLM agent
│   ├── planning_agent.py    # Learning path planning
│   └── loop_agent.py        # Iterative refinement
│
├── services/                 # Business logic
│   ├── orchestrator.py      # Agent orchestration
│   └── session_service.py   # Session management
│
├── tools/                    # Specialized tools
│   ├── custom_tool.py       # Study planner
│   ├── code_exec_tool.py    # Code execution
│   └── search_tool.py       # Web search
│
├── memory/                   # Persistence layer
│   ├── memory_manager.py    # CRUD operations
│   └── memory_store.json    # Data storage
│
├── observability/            # Monitoring
│   ├── logger.py            # Structured logging
│   └── metrics.py           # Metrics collection
│
├── frontend/                 # Web interface
│   ├── index.html           # Main page
│   ├── styles.css           # Styling
│   └── app.js               # Client logic
│
├── logs/                     # Application logs (auto-generated)
├── metrics/                  # Metrics data (auto-generated)
└── memory/                   # Session data (auto-generated)
```

## Installation

### Requirements

- Python 3.8+
- pip

### Setup

```
git clone https://github.com/Vasu-uu/PathMentor.git
cd PathMentor
pip install -r requirements.txt
```

### Configure API Key (optional)

Create `.env` and add:

```
GOOGLE_API_KEY=your_key_here
```

### Run Application

```
python app.py
```

Open in browser:

```
http://localhost:5000
```

## Example Usage

- "Create a study plan for Python in 4 weeks"
- "Explain blockchain fundamentals"
- "Run this Python code to check prime numbers"
- "Search new trends in AI"

