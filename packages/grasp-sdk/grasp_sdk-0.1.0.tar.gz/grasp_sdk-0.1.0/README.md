# Grasp SDK - Python Implementation

🐍 Python implementation of Grasp SDK for E2B platform providing secure command execution and browser automation in isolated cloud environments.

## 🚀 Features

- **Secure Execution**: Run commands and scripts in isolated E2B sandboxes
- **Browser Automation**: Control Chromium browsers with Playwright integration
- **Async/Await Support**: Full async/await support for modern Python development
- **Type Safety**: Complete type hints with Pydantic models
- **WebSocket Communication**: Real-time communication with sandbox environments
- **Multi-language Support**: Compatible with Node.js/TypeScript version

## 📦 Installation

```bash
# Install from PyPI (when published)
pip install grasp-sdk

# Install from source
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## 🔧 Quick Start

```python
import asyncio
from grasp_sdk import GraspServer

async def main():
    # Initialize Grasp server
    server = GraspServer({
        "key": api_key,
        "timeout": 30000,
    })
    
    try:
        # Start sandbox
        await server.start()
        
        # Execute command
        result = await server.execute_command("echo 'Hello from Python!'")
        print(f"Output: {result.stdout}")
        
        # Browser automation
        browser_task = await server.create_browser_task()
        await browser_task.navigate("https://example.com")
        screenshot = await browser_task.screenshot("example.png")
        
    finally:
        # Clean up
        await server.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## 🏗️ Architecture

The Python implementation mirrors the Node.js/TypeScript version:

```
py-src/
├── __init__.py              # Main package exports
├── grasp_server.py          # Main GraspServer class
├── services/                # Core services
│   ├── __init__.py
│   ├── sandbox_service.py   # E2B sandbox management
│   └── browser_service.py   # Browser automation
├── types/                   # Type definitions
│   └── __init__.py
├── utils/                   # Utilities
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── logger.py           # Logging utilities
│   └── auth.py             # Authentication
├── cli/                     # Command line interface
│   ├── __init__.py
│   └── main.py
└── tests/                   # Test suite
    └── ...
```

## 🔑 Environment Variables

```bash
# Required
E2B_API_KEY=your_e2b_api_key_here

# Optional
GRASP_LOG_LEVEL=info
GRASP_TIMEOUT=30000
GRASP_TEMPLATE=python
```

## 🧪 Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .

# Type checking
mypy .

# Linting
flake8 .
```

## 📚 API Reference

### GraspServer

Main class for interacting with E2B sandboxes and browser automation.

```python
class GraspServer:
    def __init__(self, config: ISandboxConfig = None)
    async def start(self) -> None
    async def close(self) -> None
    async def execute_command(self, command: str, options: ICommandOptions = None) -> CommandResult
    async def execute_script(self, script_path: str, options: IScriptOptions = None) -> CommandResult
    async def create_browser_task(self, config: IBrowserConfig = None) -> BrowserTask
    def get_sandbox_status(self) -> SandboxStatus
    def get_sandbox_id(self) -> str
```

## 🤝 Compatibility

This Python implementation provides the same API surface as the Node.js/TypeScript version, ensuring:

- **Feature Parity**: All features available in both implementations
- **API Consistency**: Same method names and behavior
- **Type Safety**: Equivalent type definitions using TypedDict and Pydantic
- **Error Handling**: Consistent error types and messages

## 📄 License

MIT License - see the [LICENSE](../LICENSE) file for details.

## 🔗 Related

- [Node.js/TypeScript Implementation](../src/)
- [E2B Platform](https://e2b.dev/)
- [Playwright Python](https://playwright.dev/python/)