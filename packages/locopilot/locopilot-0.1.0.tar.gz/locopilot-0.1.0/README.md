# 🚀 Locopilot

Locopilot is an open-source, local-first, agentic coding assistant built for developers. It leverages local LLMs (via Ollama or vLLM), and advanced memory management using LangGraph, to automate, plan, and edit codebases—all inside an interactive shell.

- **Private**: All code and prompts stay on your machine.
- **Agentic**: Locopilot plans, edits, iterates, and manages your coding tasks.
- **Interactive**: Drop into a shell, enter tasks or slash commands, and steer the agent in real time.
- **Memory-Efficient**: Advanced memory compression via LangGraph for "infinite" context.
- **Extensible**: Change models, modes, and add custom tools or plugins on the fly.

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Usage: Interactive Shell & Commands](#usage-interactive-shell--commands)
- [Project Structure](#project-structure)
- [Extensibility & Roadmap](#extensibility--roadmap)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **Local LLM Backend**: Bring your own Ollama or vLLM server and code with any open-source LLM.
- **LangGraph Agent Workflow**: Plans, executes, edits, and compresses memory as a stateful, extensible graph.
- **Interactive Shell/REPL**: After init, drop into a chat-like agent terminal—just type coding tasks or slash commands.
- **Slash Command Support**: `/model`, `/change-mode`, `/concise`, `/clear`, `/new`, `/end`, `/help`, and more.
- **Smart Memory Compression**: Automatically summarizes previous context using the LLM itself, supporting ultra-long sessions.
- **Configurable**: Models, modes, and summarization thresholds are all runtime-editable.
- **Pluggable Nodes**: Add file tools, planning modules, git ops, and vector-based retrieval easily.
- **(Planned) Git Integration**: Auto-commit, rollback, and view code diffs per agent step.

## ⚡️ How It Works

### 1. Initialization
Run `locopilot init` in your project root.
- Locopilot checks Ollama/vLLM, prompts for backend/model, sets up `.locopilot/config.yaml`.
- You're dropped into an interactive agent shell (REPL).

### 2. Agentic Workflow (via LangGraph)
Each user input is parsed:
- **Slash command** (`/model`, etc.) → runs as a graph branch.
- **Normal prompt** (task) → plans, edits, summarizes via a workflow graph:
  ```
  User Task → [Planning Node] → [File Edit Node] → [Memory Summarizer Node] → (Repeat)
  ```
- Memory is managed with a LangGraph memory node—summarizing, chunking, and compressing context as needed.

### 3. Session Management
- Change models, modes, or reset memory on the fly with slash commands.
- All state (memory, model, mode) persists during the session.

## 🏗️ Architecture

Key components:

- **CLI Layer**: Typer-based CLI, launches shell (REPL), parses slash commands.
- **LangGraph Workflow**:
  - **Nodes**: Planning, file edit, summarization, slash command handler, etc.
  - **Edges**: Control session flow, branching between commands and prompts.
- **LLM Backends**:
  - **Ollama**: For running CodeLlama, DeepSeek, etc.
  - **vLLM**: OpenAI-compatible, GPU-powered.
- **Memory Layer**:
  - LangChain/LangGraph memory objects (buffer, summary, vector, hybrid).
  - Summarizes old context using the LLM to avoid hitting token/window limits.
- **Config/Project Layer**:
  - `.locopilot/config.yaml` stores model/backend/session preferences.

### Stateful Graph Example:
```
               [User Input]
                      |
      +---------------+---------------+
      |                               |
 [Slash Command]              [Prompt/Task]
      |                               |
[Command Handler]   [Plan]->[Edit]->[Summarize]->[Memory]
      |                               |
     END                             Loop
```

## 🛠 Getting Started

### Requirements
- Python 3.8+
- Ollama or vLLM running locally
- pip

### Install Locopilot
```bash
git clone https://github.com/yourname/locopilot.git
cd locopilot
pip install -e .
```

### Start Your Local LLM

**Ollama:**
```bash
ollama serve
ollama pull codellama:latest
```

**vLLM:**
```bash
python -m vllm.entrypoints.openai.api_server --model <your-model>
```

### Initialize and Enter the Agent Shell
```bash
locopilot init
```

This checks LLM backend, prompts for config, scans for project context, and launches the interactive shell.

## 🖥️ Usage: Interactive Shell & Commands

After init, Locopilot enters a shell where you can type prompts and commands:

### Example Session
```
$ locopilot init
[✓] Ollama running. Model: codellama:latest
[✓] Project context initialized.

Locopilot Shell (mode: do):
> Add OAuth login to my Django app
[PLANNING] ...
[EDITING] ...
[MEMORY] ...

> /model
Current model: codellama:latest
Enter new model: deepseek-coder:latest
[✓] Model switched to deepseek-coder:latest

> /change-mode
Current mode: do
Available modes: do, refactor, explain, chat
Enter new mode: refactor
[✓] Mode set to refactor.

> Refactor the payment logic for clarity
...

> /concise
[✓] Context summarized and compressed.

> /clear
[✓] Session memory cleared.

> /new
[✓] New session started.

> /end
[✓] Session ended. Bye!
```

### Supported Slash Commands

| Command | Purpose |
|---------|---------|
| `/model` | Change LLM model/backend for current session |
| `/change-mode` | Switch between do, refactor, explain, chat modes |
| `/clear` | Clear all current context/memory |
| `/new` | Start a new session/project |
| `/end` | End the agent shell and exit |
| `/concise` | Force summarization/compression of current context |
| `/help` | Show help and command list |

Anything not starting with `/` is treated as a task in the current mode!

## 🗂️ Project Structure

```
locopilot/
├── locopilot/
│   ├── __init__.py
│   ├── cli.py            # CLI entrypoint, shell/repl logic
│   ├── agent.py          # LangGraph workflow graph and nodes
│   ├── memory.py         # Session/context memory management
│   ├── utils.py          # API, file, config helpers
│   ├── connection.py     # Ollama/vLLM connection helpers
├── tests/
│   └── test_basic.py
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

## 🧠 Memory Management (with LangGraph)

- `ConversationBufferMemory` or `ConversationSummaryBufferMemory` is attached to the agent graph.
- As session context grows, old steps are summarized using the LLM and replaced in memory.
- This ensures Locopilot "remembers" key tasks, design decisions, and context for long sessions.
- Slash command `/concise` lets you summarize on demand.

## ⚡️ Extensibility & Roadmap

- **Editor Plugins**: VSCode, Vim, JetBrains, etc.
- **Project-Aware RAG**: Integrate vector DBs (Chroma, Qdrant) for smart codebase retrieval.
- **(Planned) Git Integration**: Auto-commit, diff, and rollback per step.
- **Save/Load Sessions**: `/save`, `/load`, `/history` commands.
- **Custom Plugins/Nodes**: Add your own LangGraph nodes for tools or workflows.
- **Web/GUI Frontends**: Same agent core, different interface.

## 🤝 Contributing

- Fork and PRs are welcome!
- Open issues for bugs or feature requests.
- For major features (graph nodes, memory backends), see CONTRIBUTING.md (coming soon).

## 📝 License

MIT License. Use, fork, and extend as you wish!

## 💡 Inspiration

Locopilot is inspired by Copilot, Claude Code, Dev-GPT, OpenDevin, and the emerging open-source agentic ecosystem—aiming to empower developers with private, supercharged, customizable AI tools.

## 🚦 Quickstart

```bash
locopilot init
# ... then just type your coding tasks and manage the session with slash commands!
```