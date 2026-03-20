# Horizon Desk Developer Documentation

## Introduction
Horizon Desk allows 3rd-party developers to extend its capabilities using **Plugins**. Plugins are Python modules packaged with a metadata file (`horizon_plugin.raf`) that can register new tools for the OmniAgent.

## Plugin Structure
A valid plugin must reside in a subdirectory within the `plugins/` folder and contain at least two files:
1.  `horizon_plugin.raf` (Metadata)
2.  `plugin.py` (Python Code - entry point)

### File: `horizon_plugin.raf`
This file uses JSON format to describe your plugin. The `.raf` extension stands for **R**apnss **A**pplication **F**ile.

```json
{
    "name": "MyCoolPlugin",
    "version": "1.0.0",
    "developer": "Your Name",
    "description": "Adds cool new features to Horizon.",
    "entry_point": "plugin.py"
}
```

### File: `plugin.py`
This Python file must define a `register_tools(agent)` function. This function receives the `Agent` instance and can register new tools.

```python
from core.tools import BaseTool

class MyCustomTool(BaseTool):
    def __init__(self):
        super().__init__("MyCustomAction", "Description of what this tool does.")

    def execute(self, payload=None):
        return "Custom action executed!"

def register_tools(agent):
    agent.register_tool(MyCustomTool())
    print("MyCustomTool registered!")
```

## Available API Functions
Horizon Desk exposes several core functions and objects to developers.

### `BaseTool` Class
Located in `core.tools`. Inherit from this to create new tools.
- `__init__(self, name, description)`: Define tool name (used by AI) and description.
- `execute(self, **kwargs)`: Implement the tool logic here. Return a string result.

### `Agent` Class
The main AI agent.
- `register_tool(tool_instance)`: Adds a tool to the agent's capabilities.

### Standard Libraries
You can use standard Python libraries (`os`, `sys`, `requests`, `json`, etc.) in your plugins.

## How to Install a Plugin
1.  Create a folder in `Horizon desk/plugins/`, e.g., `plugins/MyPlugin`.
2.  Place your `horizon_plugin.raf` and `plugin.py` inside.
3.  Restart Horizon Desk (`main.py`).
4.  The plugin will be loaded automatically.
5.  Use `@list-plugins` in the CLI to verify.

## Best Practices
- **Error Handling**: Wrap your tool logic in `try-except` blocks to prevent crashing the main agent.
- **Descriptive Names**: Give your tools clear, unique names so the AI knows when to use them.
- **Security**: Do not allow arbitrary code execution or file deletion without user confirmation.

## Example: Chemical Equation Balancer
If you want to add a tool to balance equations:
1. Create `plugins/Chemistry/horizon_plugin.raf`.
2. Create `plugins/Chemistry/chemistry.py`.
3. Implement `BalanceEquationTool` in `chemistry.py`.
4. Register it in `register_tools`.

Now, when a user asks "Balance H2 + O2 -> H2O", the AI will see your tool and use it!
