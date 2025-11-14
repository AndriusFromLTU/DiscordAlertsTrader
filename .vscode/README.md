# DiscordAlertsTrader - VS Code Development Setup

This document explains the VS Code configuration for the DiscordAlertsTrader project.

## Quick Start

### 1. Using the Virtual Environment (Recommended)

The project is configured to use a Python virtual environment located at `.venv/`.

**First-time setup:**
```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

**Or use the VS Code Task:**
- Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
- Type "Run Task" and select "Setup Project"

### 2. Using Dev Container (Alternative)

If you prefer containerized development:
1. Install the "Dev Containers" extension
2. Press `Cmd+Shift+P` → "Dev Containers: Reopen in Container"
3. Wait for the container to build and dependencies to install

## VS Code Configuration

### Settings (`.vscode/settings.json`)
- **Python Interpreter**: Automatically uses `.venv/bin/python`
- **Testing**: pytest configured for the `tests/` directory
- **Formatting**: Black formatter with 88 character line limit
- **Auto-save**: Enabled with 1 second delay
- **Format on Save**: Enabled
- **Import Organization**: Auto-organizes imports on save

### Debug Configurations (`.vscode/launch.json`)

Available debug configurations:
1. **Python: DiscordAlertsTrader GUI** - Launch the main GUI application
2. **Python: Discord Bot** - Run the Discord bot directly
3. **Python: Current File** - Debug the currently open Python file
4. **Python: pytest - All Tests** - Debug all tests
5. **Python: pytest - Current File** - Debug tests in current file
6. **Python: Attach to Process** - Attach debugger to running process

### Tasks (`.vscode/tasks.json`)

Available tasks (access with `Cmd/Ctrl+Shift+P` → "Run Task"):

**Installation & Setup:**
- `Install Dependencies` - Install packages from requirements.txt
- `Install Dev Dependencies` - Install in editable mode
- `Create Virtual Environment` - Create new .venv
- `Setup Project` - Complete setup (venv + dependencies)

**Running the Application:**
- `Run DiscordAlertsTrader GUI` - Start the GUI application
- `Run Discord Bot` - Start the Discord bot

**Testing:**
- `Run Tests` - Run all pytest tests (default test task)
- `Run Tests with Coverage` - Run tests with coverage report

**Code Quality:**
- `Format Code (Black)` - Format all code with Black
- `Lint Code (Pylint)` - Run pylint on the codebase

### Recommended Extensions (`.vscode/extensions.json`)

When you open the project, VS Code will suggest installing:

**Essential:**
- Python
- Pylance (language server)
- Black Formatter
- Pylint
- Python Debugger

**Helpful:**
- autodocstring - Generate Python docstrings
- GitLens - Enhanced Git features
- GitHub Copilot - AI pair programming
- Jupyter - For notebook support
- Rainbow CSV - Better CSV viewing
- Todo Tree - Track TODO comments

## Running the Application

### From VS Code:

**Option 1: Debug Panel**
1. Go to Run & Debug panel (`Cmd/Ctrl+Shift+D`)
2. Select "Python: DiscordAlertsTrader GUI"
3. Click the green play button

**Option 2: Tasks**
1. Press `Cmd/Ctrl+Shift+P`
2. Type "Run Task"
3. Select "Run DiscordAlertsTrader GUI"

**Option 3: Terminal**
```bash
# Make sure venv is activated or use:
.venv/bin/python -m DiscordAlertsTrader.gui
```

## Testing

### Run All Tests:
```bash
.venv/bin/pytest tests -v
```

### Run with Coverage:
```bash
.venv/bin/pytest tests --cov=DiscordAlertsTrader --cov-report=html
```

### Using VS Code:
- Press `Cmd/Ctrl+Shift+P` → "Run Task" → "Run Tests"
- Or use the Test Explorer in the sidebar

## Development Workflow

1. **Start Coding**: Open the project, VS Code will detect the virtual environment
2. **Format**: Code is auto-formatted on save with Black
3. **Test**: Run tests frequently using the Test task or debug configuration
4. **Debug**: Set breakpoints and use the debug configurations
5. **Lint**: Run the Lint task to check code quality

## Troubleshooting

### "Module not found" errors:
```bash
# Reinstall dependencies
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e .
```

### GUI not launching:
Ensure PySide6 is installed:
```bash
.venv/bin/pip install PySide6
```

### Python interpreter not detected:
1. Press `Cmd/Ctrl+Shift+P`
2. Type "Python: Select Interpreter"
3. Choose `.venv/bin/python`

### Dev Container issues on macOS:
For GUI applications, the dev container requires X11 forwarding. For local development, using the virtual environment is recommended.

## Project Structure

```
DiscordAlertsTrader/
├── .devcontainer/          # Container configuration
├── .vscode/                # VS Code settings
├── DiscordAlertsTrader/    # Main package
├── tests/                  # Test files
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
└── setup.py               # Package setup
```

## Additional Resources

- **Main README**: See [README.md](../README.md) for project documentation
- **Setup TDA**: Run `setup_TDA.py` for TD Ameritrade configuration
- **Configuration**: Copy `config_example.ini` to `config.ini` and customize
