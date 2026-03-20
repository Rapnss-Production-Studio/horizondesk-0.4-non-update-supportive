# OmniAgent: Massive Agentic Framework (CLI)

OmniAgent is a powerful, extensible AI framework designed to control your computer using ReAct logic and Vision models.

## Features
-   **ReAct Logic**: Reasons about steps before acting.
-   **Vision Capable**: Can "see" your screen and click buttons.
-   **Desktop Automation**: Opens apps, manages files, clicks mouse.
-   **Extensible**: Easy to add new tools in `tools/`.

## Setup
1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configure Environment**:
    -   Ensure `.env` contains your `GROQ_API_KEY`.
3.  **Run**:
    ```bash
    python main.py
    ```

## Usage
Once the CLI starts, you can give natural language commands:

> **User**: "Open Notepad and write a poem about AI."
> **Agent**: *Launches Notepad, types poem.*

> **User**: "Take a screenshot and tell me what you see."
> **Agent**: *Takes screenshot, analyzes it with Vision LLM.*

> **User**: "Clean up my desktop by moving all text files to a Documents folder."
> **Agent**: *Lists files, creates folder, moves files.*

## Architecture
-   `core/agent.py`: The brain.
-   `core/llm.py`: Interface to Groq (Llama 3 Text + Vision).
-   `tools/`: Directory of capabilities.
