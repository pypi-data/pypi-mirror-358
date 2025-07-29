# Stability Toolkit for LangChain

A production-ready toolkit that enables AI agents to interact with the Stability blockchain without gas fees or cryptocurrency requirements.

## ✨ Production-Ready Features (Latest Update)

- **🔑 Environment Variable Support**: Set `STABILITY_API_KEY` for production deployments
- **🛠️ Flexible Configuration**: Initialize with custom API keys or use environment variables
- **🔒 Security Enhancements**: API key sanitization in logs and error messages
- **⚠️ Production Warnings**: Helpful guidance for production vs. development usage
- **📚 Comprehensive Documentation**: Clear examples and best practices

## 🚀 Quick Start

### Installation

```bash
pip install langchain-core requests
```

### Basic Usage

```python
from stability_toolkit import StabilityToolkit

# Option 1: Using environment variable (recommended for production)
export STABILITY_API_KEY="your-api-key"
toolkit = StabilityToolkit()

# Option 2: Direct API key (for development/testing)
toolkit = StabilityToolkit(api_key="your-api-key")

# Get all tools
tools = toolkit.get_tools()
```

## 🔑 API Key Setup

### Getting Your FREE API Key

1. **Visit the Stability Protocol Portal**: [https://portal.stabilityprotocol.com/](https://portal.stabilityprotocol.com/)
2. **Sign up for a free account**
3. **Generate your API key(s)**

### Free Tier Limits
- **🔢 API Keys**: Up to 3 keys per account
- **✍️ Write Transactions**: 1,000 per month
- **📖 Read Operations**: 200 per minute
- **💰 Cost**: Completely FREE

### Setting Up Your API Key

#### Option 1: Environment Variable (Recommended)
```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export STABILITY_API_KEY="your-api-key-from-portal"

# Or set for current session
export STABILITY_API_KEY="your-api-key-from-portal"
```

#### Option 2: Direct Configuration
```python
from stability_toolkit import StabilityToolkit

toolkit = StabilityToolkit(api_key="your-api-key-from-portal")
```

#### Option 3: Development/Testing
```python
# Uses "try-it-out" key with limited functionality
toolkit = StabilityToolkit()
```

## 🛠️ Available Tools

1. **StabilityWriteTool** - Send messages to blockchain
2. **StabilityReadTool** - Read from smart contracts  
3. **StabilityWriteContractTool** - Write to smart contracts
4. **StabilityDeployTool** - Deploy Solidity contracts

## 🔧 API Key Configuration

### Environment Variable (Recommended)
```bash
export STABILITY_API_KEY="your-api-key"
```

### Programmatic Configuration
```python
toolkit = StabilityToolkit(api_key="your-api-key")
```

### Development/Testing
```python
# Uses "try-it-out" key with limited functionality
toolkit = StabilityToolkit()
```

## 🔒 Security Features

- **API Key Sanitization**: Keys are automatically sanitized in logs and error messages
- **Environment Variable Support**: Secure configuration without hardcoding keys
- **Production Warnings**: Clear guidance on API key limitations and best practices

## 📞 Support & Contact

- **Support Email**: [contact@stabilityprotocol.com](mailto:contact@stabilityprotocol.com)
- **API Portal**: [https://portal.stabilityprotocol.com/](https://portal.stabilityprotocol.com/)
- **Documentation**: Comprehensive examples and usage patterns included

**StabilityToolkit** is a LangChain-compatible toolkit that enables AI agents to interact directly with the [Stability Blockchain](https://stabilityprotocol.com) through Zero Gas Transaction (ZKT) API endpoints. It includes tools for submitting simple messages, interacting with smart contracts (read/write), and deploying contracts — all without requiring gas fees or cryptocurrency.

---

## 🚀 Features

* ✅ Write plain messages to Stability (ZKT)
* ✅ Read smart contract data (ZKT Simple - view)
* ✅ Call smart contract functions (ZKT Simple - write)
* ✅ Deploy new smart contracts (ZKT Contract)
* ✅ Works with public and authenticated endpoints

---

## 🛠 Tools Overview

| Tool Name                    | Description                                      |
| ---------------------------- | ------------------------------------------------ |
| `StabilityWriteTool`         | POSTs a string message to the blockchain         |
| `StabilityReadTool`          | Reads data from smart contracts via ABI & method |
| `StabilityWriteContractTool` | Calls smart contract write methods               |
| `StabilityDeployTool`        | Deploys Solidity smart contracts to Stability    |

---

## 🧱 Installation

```bash
pip install langchain openai requests
```

---

## 🧪 Example Usage

```python
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent
from stability_toolkit import StabilityToolkit

llm = ChatOpenAI(model="gpt-4o", temperature=0)
toolkit = StabilityToolkit()
agent = initialize_agent(toolkit.get_tools(), llm, agent_type="zero-shot-react-description")

response = agent.run("Deploy a contract that stores a greeting and a value")
print(response)
```

---

## 🧪 Running Tests

```bash
# Run live blockchain tests
python -m unittest test_stability_toolkit_live.py

# Run LangChain integration tests  
python -m unittest test_stability_toolkit_langchain.py
```

---

## 🔐 API Keys

* Public endpoint: `https://rpc.stabilityprotocol.com/zkt/try-it-out`
* Get your free personal key at [portal.stabilityprotocol.com](https://portal.stabilityprotocol.com)
* Replace `try-it-out` in URLs with your API key to sign with your own identity.

---

## 📄 API Docs

For full OpenAPI documentation, see:
[https://stabilityprotocol.github.io/stability-api-docs](https://stabilityprotocol.github.io/stability-api-docs)

---

## 💡 Contribution Ideas

* Add retry logic or exponential backoff
* Support transaction result polling with `wait=True`
* Extend Toolkit with `StatusTool` or `VerifyTool`
* Add automatic schema validation with `pydantic`

---

## 📬 Contact

For questions, feature requests, or contributions, reach out via [stabilityprotocol.com](https://stabilityprotocol.com)
