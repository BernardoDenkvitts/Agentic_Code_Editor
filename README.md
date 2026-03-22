<div align="center">
  <h1>🤖 Agentic Code Editor</h1>
  <p><i>A minimal, pure-Python multi-agent system that autonomously modifies code based on your natural language tasks.</i></p>
  
  [![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
  [![API](https://img.shields.io/badge/LLM-Groq-orange.svg)](https://groq.com/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
</div>

---

**Agentic Code Editor** is built from scratch without orchestration frameworks like LangGraph. The agent pipeline is explicit and easy to follow: agents communicate through structured JSON and a shared history object, ensuring transparency and control over the whole process.

## How It Works

When you run the system, a control loop starts. At each iteration, the **Orchestrator** inspects the current history and decides which agent should act next. The pipeline always follows this rigorous order:

<div align="center">
  <code>read → plan → code → finish</code>
</div>
<br>

Each step is handled by a specialized, dedicated agent:

- 📖 **1. Reader** — Scans the target project folder and loads all source files into memory (Python, JS, TS, Go, etc.). *Purely deterministic, no LLM involved.*
- 🧠 **2. Planner** — Analyzes the task description and the full codebase to produce a structured JSON plan, detailing exactly which files to touch and what to change.
- 💻 **3. Coder** — Translates the plan into JSON patches with line-level operations (`replace`, `insert`, `delete`).
- 🎼 **4. Orchestrator** — A lightweight LLM agent that reads the current history and decides the next action. It is stateless; all context lives in the history array.
- 🕵️ **5. Reviewer** *(Optional)* — An LLM-based code reviewer. It analyzes the full multi-file diff and returns `approved` or `rejected` with detailed reasoning before applying patches.
- 🛠️ **6. Patcher** — A robust utility (non-LLM) that safely applies the approved patch operations to your actual source files.

## 📂 Project Structure

<details>
<summary><b>Click to expand the directory tree</b></summary>
<br>

```text
src/
├── main.py               # Entry point and main control loop
├── llm.py                # LLM client wrapper (Groq + caching)
├── history.py            # Renders history and codebase into prompt-friendly text
├── patcher.py            # Applies patches to files and saves the report
└── agents/
    ├── orchestrator.py   # Decides the next action based on current history
    ├── reader.py         # Scans the project folder and loads file contents
    ├── planner.py        # Produces a JSON change plan from the task + codebase
    ├── coder.py          # Generates line-level patch operations for each file
    └── reviewer.py       # Reviews the diff and approves or rejects the changes
```
</details>

## 🚀 Demo

Here's how the console output looks during a live execution:

> **Execution Terminal:**
<div align="center">
  <img src="console_demo.png" alt="Terminal execution demonstration" width="850"/>
</div>

## 🛠️ Usage

### 1. Installation

Clone the repository and install dependencies using `uv`:

```bash
git clone https://github.com/BernardoDenkvitts/Agentic_Code_Editor.git
cd Agentic_Code_Editor
uv sync
```

### 2. Configuration

Set up your [Groq](https://groq.com/) API key:

```bash
export GROQ_API_KEY="<your_api_key>"
```
*(Alternatively, create a `.env` file in the `src/` directory).*

### 3. Running an Agent Task

Navigate to the `src` folder and run the `main.py` entrypoint.

```bash
cd src
uv run main.py --project ../sample_project_1 --task "Fix the bug where passwords are stored in plain text"
```

#### Command-Line Options

| Flag | Short | Description |
| :--- | :---: | :--- |
| `--project` | `-p` | Path to the target project folder you want to modify |
| `--task` | `-t` | Natural language description of the requested changes |
| `--files` | `-f` | *(Optional)* Restrict the agent to specifically named files |

#### Examples

**Targeting specific files:**
```bash
uv run main.py -p ../sample_project_2 -t "The confirmation email does not include the order ID or total. Fix send_confirmation_email to receive and display both." -f notifier.py, order_processor.py
```

**Whole project context:**
```bash
uv run main.py -p ../sample_project_1 -t "Refactor the authentication logic"
```

## 🧠 LLM and Caching

This system is powered by **[Groq](https://groq.com/)** using the `qwen/qwen3-32b` model.

To avoid redundant API calls and speed up testing, all calls to the **Planner** and **Coder** are aggressively cached locally in `src/.cache/` (using an MD5 hash of the prompt). *Note: The Orchestrator and Reviewer bypass the cache to maintain dynamic behavior.*

## 📦 Dependencies

| Package | Purpose |
| :--- | :--- |
| `groq` | Official LLM API client |
| `rich` | Beautiful terminal formatting & outputs |
| `python-dotenv` | Loads environment variables from a `.env` file |

---

<div align="center">
  <i>💡 Note: <code>sample_project_1/</code> and <code>sample_project_2/</code> are included at the repository root for testing and experimentation.</i>
</div>
