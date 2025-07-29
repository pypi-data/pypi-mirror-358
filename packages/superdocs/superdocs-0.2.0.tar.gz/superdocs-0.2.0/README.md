# SuperDocs - Enhanced MCP Documentation Server

## Overview

**SuperDocs** is an enhanced version of the MCP LLMS-TXT Documentation Server with additional superpowers! 🚀

[llms.txt](https://llmstxt.org/) is a website index for LLMs, providing background information, guidance, and links to detailed markdown files. IDEs like Cursor and Windsurf or apps like Claude Code/Desktop can use `llms.txt` to retrieve context for tasks. However, these apps use different built-in tools to read and process files like `llms.txt`. The retrieval process can be opaque, and there is not always a way to audit the tool calls or the context returned.

[MCP](https://github.com/modelcontextprotocol) offers a way for developers to have *full control* over tools used by these applications. **SuperDocs** extends the original mcpdoc with enhanced features and better performance.

## ✨ SuperDocs Features

- 🔍 **Enhanced documentation parsing**
- 🚀 **Better performance and caching**
- 📚 **Extended format support**
- 🛡️ **Improved security**
- 🔧 **Custom integrations**
- 🧭 **Hierarchical navigation with browse_page** (NEW in v0.2.0)

## Installation

### Quick Start with uvx (Recommended)

```bash
uvx --from superdocs superdocs \
    --urls "LangGraph:https://langchain-ai.github.io/langgraph/llms.txt" \
    --transport stdio
```

### Install from PyPI

```bash
pip install superdocs
```

## Usage

### Command Line

```bash
# Basic usage
superdocs --urls "LangGraph:https://langchain-ai.github.io/langgraph/llms.txt"

# Multiple sources
superdocs --urls "LangGraph:https://langchain-ai.github.io/langgraph/llms.txt" "LangChain:https://python.langchain.com/llms.txt"

# Using config file
superdocs --yaml config.yaml
```

### MCP Configuration

#### Cursor

Add to your `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "superdocs": {
      "command": "uvx",
      "args": [
        "--from",
        "superdocs",
        "superdocs",
        "--urls",
        "LangGraph:https://langchain-ai.github.io/langgraph/llms.txt",
        "--transport",
        "stdio"
      ]
    }
  }
}
```

#### Windsurf

Add to your `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "superdocs": {
      "command": "uvx",
      "args": [
        "--from",
        "superdocs", 
        "superdocs",
        "--urls",
        "LangGraph:https://langchain-ai.github.io/langgraph/llms.txt",
        "--transport",
        "stdio"
      ]
    }
  }
}
```

#### Claude Desktop

Add to your `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "superdocs": {
      "command": "uvx",
      "args": [
        "--from",
        "superdocs",
        "superdocs", 
        "--urls",
        "LangGraph:https://langchain-ai.github.io/langgraph/llms.txt",
        "--transport",
        "stdio"
      ]
    }
  }
}
```

## 🔧 Development

### Local Development

```bash
git clone https://gitlab.com/nikakoss23/superdocs.git
cd superdocs
uv venv
source .venv/bin/activate  # На Windows: .venv\Scripts\activate
uv pip install -e ".[test]"
```

### Running Tests

```bash
pytest tests/
```

### Building

```bash
uv build
```

## 🚀 Contributing

1. Fork the project on GitLab
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Merge Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Based on the original [mcpdoc](https://github.com/langchain-ai/mcpdoc) by LangChain AI.

## 📚 Documentation

For more information about the Model Context Protocol, see:
- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Specification](https://spec.modelcontextprotocol.io/)

---

Made with ❤️ by [Agentium](https://agentium.ru)
