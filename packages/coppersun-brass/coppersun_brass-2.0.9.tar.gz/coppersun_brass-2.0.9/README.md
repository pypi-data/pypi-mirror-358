# Copper Sun Brass

> 🧠 Development Intelligence for AI Agents

Copper Sun Brass is an AI advisory system that acts as a "General Staff" for AI agents (like Claude or GPT) working on software projects. It provides persistent memory, project analysis, and intelligence gathering.

## 🚀 Quick Start

```bash
# Install Copper Sun Brass
pip install -e .

# Activate with license
brass activate BRASS-DEVL-SCOTT-INTERNAL-2025

# Configure Claude API (required)
brass config set claude_api_key sk-your-api-key

# Initialize in your project
cd your-project
brass init

# Check status  
brass status

# Get insights
brass insights
```

## 🎯 Key Features

### Four Specialized Agents

1. **Watch Agent** 👁️ - Continuous project monitoring
2. **Scout Agent** 🔍 - Deep code analysis and pattern detection  
3. **Strategist Agent** 🎯 - High-level planning and recommendations
4. **Planner Agent** 📋 - Task generation and prioritization

### Core Capabilities

- **Persistent Memory** 💾 - Maintains context across AI sessions
- **Strategic Planning** 📊 - Project analysis and recommendations
- **Pattern Detection** 🔍 - Identifies code patterns and potential issues
- **File System Monitoring** 📡 - Tracks file changes
- **Code Intelligence** 🧠 - Pattern-based analysis and security detection
- **Privacy-First** 🔒 - All data stays local

## 📖 Documentation

> **📁 Documentation Structure**: All current documentation is in [`docs/`](docs/) - see [`docs/README.md`](docs/README.md) for complete index

### For Users
- [Getting Started](docs/getting-started.md) - Installation and first steps
- [User Guide](docs/user-guide.md) - Comprehensive feature guide
- [CLI Reference](docs/CLI_REFERENCE.md) - Complete command documentation

### For Developers  
- [Developer Guide](docs/developer-guide.md) - Development environment setup
- [Architecture](docs/architecture.md) - System design and components
- [Testing](docs/testing/README.md) - Testing framework and guides

### Migration
- [Migration from DevMind](docs/migration-from-devmind.md) - Complete migration instructions

### AI Agents (Claude Code Users)
- **Start Here**: [`CLAUDE.md`](CLAUDE.md) - Essential orientation for AI agents
- **Project Status**: Always check actual files - don't assume anything
- **Documentation**: Use [`docs/`](docs/) for current, verified information

## 🔧 Installation Options

### Basic Installation
```bash
# Core features only
pip install -e .
```

### Full Installation
```bash
# Including ML models and all features
pip install -e .[all]
```

### Development Installation
```bash
# For contributing
pip install -e .[dev]
```

## 💡 Usage Examples

### Basic Workflow
```bash
# Check project health
brass status

# Get insights and recommendations
brass insights

# Refresh project context
brass refresh

# Update AI instructions
brass update-ai
```

### CI/CD Integration
```python
# In your CI pipeline
import subprocess
result = subprocess.run(["brass", "status"], 
                       capture_output=True)
# Process results...
```

## 🏗️ Project Structure

```
coppersun_brass/
├── src/coppersun_brass/    # Source code
│   ├── agents/               # The four agents
│   ├── core/                 # Core functionality
│   ├── cli/                  # Command-line interface
│   └── ml/                   # ML components
├── config/                   # Configuration files
├── docs/                     # Documentation
│   ├── implementation/      # Implementation guides
│   ├── planning/           # Planning documents
│   └── testing/            # Testing documentation
├── examples/                 # Usage examples
├── tests/                    # Test suite
├── scripts/                  # Utility scripts
├── docker/                 # Docker configuration
├── k8s/                    # Kubernetes manifests
├── archive/                # Historical development artifacts
└── README.md              # This file
```

## 🔄 Migration from DevMind

If you're migrating from DevMind, see our [Migration Guide](docs/migration-from-devmind.md). Your licenses and configuration will work automatically.

## 🛡️ License

Copper Sun Brass requires a license for production use:
- **Trial**: 30-day evaluation
- **Developer**: For individual developers
- **Team**: For development teams
- **Enterprise**: Custom solutions

See [License Guide](docs/license-guide.md) for details.

## 🤝 Contributing

We welcome contributions! See [Contributing Guide](docs/contributing.md) for:
- Development setup
- Code standards
- Testing requirements
- Pull request process

## 🆘 Getting Help

- **Documentation**: Start with our [docs](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/coppersun-brass/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/coppersun-brass/discussions)

## 🌟 Why Copper Alloy Brass?

Traditional development tools are stateless. AI agents forget context between sessions. Copper Alloy Brass solves this by providing:

1. **Persistent Intelligence**: Never lose context
2. **Strategic Thinking**: Beyond syntax checking
3. **Adaptive Learning**: Improves with your project
4. **AI-Native Design**: Built for AI, not humans

## 📊 Status

- **Version**: 2.0.0
- **Status**: Development/Beta
- **Python**: 3.8+
- **License**: Proprietary (see LICENSE)

## 🙏 Acknowledgments

**Third-Party Tools & Services:**
- **Microsoft CodeBERT** - Code understanding models (MIT License)
- **HuggingFace Transformers** - Model loading and inference (Apache 2.0)
- **Claude API** - AI analysis capabilities

**Disclaimer:**
Claude and Claude Code are products of Anthropic PBC. Brass is an independent development intelligence tool that works with various AI coding assistants, including Claude Code, and is not affiliated with Anthropic.

---

**Ready to enhance your AI development workflow?** 🚀

```bash
brass init && brass status
```

*Built with ❤️ for AI agents and the developers who work with them.*