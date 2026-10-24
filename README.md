# Multi-Tool AI Agent 🤖

A Python-based AI agent designed to use multiple tools to perform tasks and answer user questions. The project is being developed step by step, starting with standalone Python tools and progressing toward an LLM-powered agent that can select and execute tools intelligently.

## 🚀 Project Goals

- Build an AI agent that can use multiple tools.
- Integrate a locally running Large Language Model (LLM).
- Implement intelligent tool selection and execution.
- Provide a simple conversational interface.
- Develop a modular, testable, and extensible application.

## 🛠️ Technology Stack

- **Python** — Core programming language
- **Ollama** — Local LLM execution
- **Qwen 2.5 7B** — Planned language model for tool selection
- **FastAPI** — Planned backend API
- **Streamlit** — Planned user interface
- **Git & GitHub** — Version control and project hosting

## ✨ Current Features

- [x] Calculator tool for basic arithmetic operations
- [x] Division-by-zero error handling
- [x] Date and time tool
- [x] Separate test scripts for individual tools
- [ ] Web search integration
- [ ] Weather information tool
- [ ] LLM-based tool selection
- [ ] Automated tool execution and response generation
- [ ] FastAPI backend
- [ ] Interactive chat interface
- [ ] Comprehensive automated testing
- [ ] Deployment

## 📁 Project Structure

```text
Multi-Tool-AI-Agent/
├── agent/
├── tools/
│   ├── calculator.py
│   └── datetime_tool.py
├── tests/
├── test_calculator.py
├── test_datetime.py
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

*Note: The structure will evolve as new components are implemented.*

## ⚙️ Getting Started

### Prerequisites

- Python 3.11 or later
- Git
- Ollama (required when the LLM integration is implemented)

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Multi-Tool-AI-Agent
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual GitHub repository URL.

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Test the calculator tool

```powershell
python test_calculator.py
```

### 5. Test the date and time tool

```powershell
python test_datetime.py
```

## 🧠 How It Will Work

The planned agent architecture follows this workflow:

1. The user submits a question.
2. The LLM interprets the request.
3. The agent selects the appropriate tool.
4. The selected tool executes the task.
5. The agent processes the tool's result.
6. The LLM generates a response for the user.

## 🎯 Learning Objectives

This project explores practical AI engineering concepts, including:

- Python functions and modular programming
- Tool design and execution
- LLM integration and tool calling
- Agent workflows and decision-making
- API development and integration
- Error handling and testing
- Version control and deployment

## 🔮 Future Improvements

- Add more tools and integrations.
- Support multi-step tool execution.
- Implement conversation history and memory.
- Add tool-call validation and execution limits.
- Improve reliability and error handling.
- Deploy the application for public access.

## 👨‍💻 Author

**Syed Ali Hassan**

Software Engineering Graduate | Aspiring AI Engineer

- GitHub: [Ali241124](https://github.com/Ali241124)
- Portfolio: [syedalihassan-portfolio.vercel.app](https://syedalihassan-portfolio.vercel.app/)

## 📄 License

This project is currently under development. A license can be added once the preferred licensing terms have been selected.
