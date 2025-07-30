# MCP Clients

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/faizraza/mcp-clients)

A powerful and easy-to-use Python package for creating **Model Context Protocol (MCP)** clients that seamlessly integrate with AI models and external tools. Currently supports Google's **Gemini AI** with plans for additional model integrations.

## 🚀 Features

- **🤖 Gemini AI Integration**: Built-in support for Google's Gemini models
- **🔗 MCP Protocol Support**: Seamless integration with MCP servers
- **🛠️ Tool Calling**: Automatic tool discovery and execution
- **💬 Interactive Chat**: Built-in chat interface with conversation history
- **🎨 Customizable**: Support for custom chat loops and system instructions
- **🔧 Easy Setup**: Simple configuration with environment variables
- **⚡ Async/Await**: Fully asynchronous for optimal performance

## 📦 Installation

Install using pip:

```bash
pip install mcp-clients
```

Or install from source:

```bash
git clone https://github.com/yourusername/mcp-clients
cd mcp-clients
pip install -e .
```

## 🔧 Prerequisites

- **Python 3.12+**
- **Google Gemini API Key** - Get yours from [Google AI Studio](https://makersuite.google.com/)
- **MCP Server** - A Model Context Protocol server (Python or JavaScript)

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in your project root:

```env
# Required: Your Gemini API key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Default MCP server path
MCP_SERVER=/path/to/your/mcp_server.py
```

### API Key Setup

1. Visit [Google AI Studio](https://makersuite.google.com/)
2. Create a new API key
3. Add it to your `.env` file or pass it directly to the client

## 🚀 Quick Start

### Basic Usage

```python
import asyncio
from dotenv import load_dotenv
from mcp_clients import Gemini

load_dotenv()

async def main():
    # Initialize the client
    client = await Gemini.init(
        server_script_path='path/to/your/mcp_server.py',
        system_instruction='You are a helpful assistant.'
    )
    
    try:
        # Start interactive chat
        await client.chat_loop()
    finally:
        # Clean up resources
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

### Programmatic Usage

```python
import asyncio
from mcp_clients import Gemini

async def query_example():
    client = await Gemini.init(
        api_key="your-api-key",
        server_script_path="weather_server.py",
        system_instruction="You are a weather assistant."
    )
    
    try:
        # Process a single query
        response = await client.process_query("What's the weather like in New York?")
        print(response)
        
        # Process multiple queries
        queries = [
            "Tell me about the weather in California",
            "Are there any weather alerts for Texas?"
        ]
        
        for query in queries:
            response = await client.process_query(query)
            print(f"Q: {query}")
            print(f"A: {response}\n")
            
    finally:
        await client.cleanup()

asyncio.run(query_example())
```

### Custom Chat Loop

```python
async def custom_chat_handler(client):
    """Custom chat loop with enhanced features"""
    print("🤖 Enhanced Chat Started!")
    print("Commands: 'help', 'history', 'clear', 'quit'")
    
    while True:
        try:
            query = input("\n💬 You: ").strip()
            
            if query.lower() == 'quit':
                break
            elif query.lower() == 'help':
                print("Available commands: help, history, clear, quit")
                continue
            elif query.lower() == 'history':
                print(f"Conversation has {len(client.history)} messages")
                continue
            elif query.lower() == 'clear':
                client.history = []
                print("Chat history cleared!")
                continue
                
            response = await client.process_query(query)
            print(f"🤖 Assistant: {response}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")

# Use the custom chat loop
async def main():
    client = await Gemini.init(
        server_script_path='weather_server.py',
        custom_chat_loop=custom_chat_handler
    )
    
    try:
        await client.chat_loop()
    finally:
        await client.cleanup()
```

## 📚 API Reference

### Gemini Class

The main client class for interacting with Gemini AI through MCP servers.

#### Initialization

```python
client = await Gemini.init(
    api_key=None,                    # Gemini API key (or use env var)
    server_script_path=None,         # Path to MCP server script
    model="gemini-2.5-flash",        # Gemini model to use
    system_instruction=None,         # Custom system instruction
    custom_chat_loop=None            # Custom chat loop function
)
```

#### Methods

- **`process_query(query: str) -> str`**: Process a single query
- **`chat_loop()`**: Start interactive chat session
- **`cleanup()`**: Clean up resources (always call this!)
- **`connect_to_server()`**: Manually connect to MCP server

## 🛠️ MCP Server Example

Here's a simple weather MCP server example:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

@mcp.tool()
async def get_weather(city: str) -> str:
    """Get weather information for a city."""
    # Your weather API logic here
    return f"The weather in {city} is sunny and 72°F"

@mcp.tool()
async def get_forecast(city: str, days: int = 3) -> str:
    """Get weather forecast for a city."""
    # Your forecast logic here
    return f"3-day forecast for {city}: Sunny, Partly Cloudy, Rainy"

if __name__ == "__main__":
    mcp.run()
```

## 📁 Project Structure

```
mcp-clients/
├── mcp_clients/
│   ├── __init__.py          # Package initialization and exports
│   ├── gemini.py           # Gemini client implementation
│   └── version.py          # Version information
├── examples/
│   └── quickstart.py       # Quick start example
├── tests/                  # Test files (coming soon)
├── README.md               # This file
├── pyproject.toml          # Project configuration
└── .env.example           # Environment variables example
```

## 🔍 Troubleshooting

### Common Issues

1. **API Key Errors**
   ```
   Error: Invalid API key
   ```
   - Ensure your Gemini API key is correct
   - Check that the API key is properly set in your environment

2. **Server Connection Issues**
   ```
   Error: Server script must be a .py or .js file
   ```
   - Verify your MCP server script path is correct
   - Ensure the file has the proper extension (.py or .js)

3. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'mcp_clients'
   ```
   - Install the package: `pip install mcp-clients`
   - If installing from source: `pip install -e .`

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🧪 Examples

Check out the `examples/` directory for more usage examples:

- **Basic Usage**: Simple chat with MCP tools
- **Weather Bot**: Weather information assistant
- **Custom Tools**: Creating and using custom MCP tools

## 🚧 Roadmap

- [ ] **Additional Model Support**: OpenAI GPT, Anthropic Claude
- [ ] **Advanced Tool Management**: Tool discovery and validation
- [ ] **Streaming Responses**: Real-time response streaming
- [ ] **Session Management**: Persistent conversation sessions
- [ ] **Plugin System**: Extensible plugin architecture
- [ ] **Web Interface**: Optional web-based chat interface

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/mcp-clients.git
   cd mcp-clients
   ```

2. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   pip install -r requirements-dev.txt
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Development Guidelines

- **Code Style**: Follow PEP 8 and use `black` for formatting
- **Type Hints**: Add type hints to all functions and methods
- **Documentation**: Add docstrings and update README if needed
- **Testing**: Write tests for new features (pytest)
- **Commits**: Use conventional commit messages

### Types of Contributions

- 🐛 **Bug Fixes**: Fix issues and improve stability
- ✨ **New Features**: Add new models, tools, or capabilities
- 📚 **Documentation**: Improve docs, examples, and tutorials
- 🧪 **Testing**: Add tests and improve test coverage
- 🎨 **UI/UX**: Improve user experience and interfaces

### Submitting Changes

1. **Run tests** (when available)
   ```bash
   pytest
   ```

2. **Format code**
   ```bash
   black mcp_clients/
   ```

3. **Submit a pull request**
   - Describe your changes clearly
   - Link any related issues
   - Include examples if applicable

### Code of Conduct

Please be respectful and inclusive. We're building this together! 🌟

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google** for the Gemini AI API
- **Anthropic** for the Model Context Protocol specification
- **FastMCP** for the excellent MCP server framework
- **Contributors** who help make this project better

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/mcp-clients/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mcp-clients/discussions)
- **Email**: your.email@example.com

---

**Made with ❤️ by [Muhammad Faiz Raza](https://github.com/faizrazadec)**

*If you find this project helpful, please consider giving it a ⭐ on GitHub!*
