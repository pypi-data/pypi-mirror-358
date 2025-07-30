# 📊 Syft-Datasets

Interactive dataset discovery and management for SyftBox applications with beautiful Jupyter UI

## 🚀 Overview

Syft-Datasets provides an intuitive way to discover, explore, and work with datasets in the SyftBox federated learning ecosystem. It bridges the gap between SyftBox's powerful data management capabilities and familiar data science workflows.

### Key Features

- 🎨 **Beautiful Jupyter Interface** - Interactive HTML tables with search, filtering, and selection
- 🔍 **Smart Dataset Discovery** - Automatically finds datasets across your connected datasites
- 📋 **Easy Selection** - Checkbox interface with automatic code generation
- 🔗 **OpenAI-Compatible API** - Familiar chat completions interface using datasets as models
- 🌐 **Cross-Platform** - Works seamlessly across different SyftBox installations
- 🛡️ **Privacy-First** - Respects SyftBox's privacy and security model

## 📦 Installation

```bash
pip install syft-datasets
```

## 🎯 Quick Start

### Basic Usage

```python
import syft_datasets as syd

# Interactive dataset browsing in Jupyter
syd.datasets  # Shows beautiful HTML table

# Search for specific datasets
crop_data = syd.datasets.search("crop")
user_data = syd.datasets.filter_by_email("andrew@openmined.org")

# Get datasets by index
first_three = syd.datasets[:3]
specific_ones = syd.datasets.get_by_indices([0, 2, 5])
```

### Dataset Properties

```python
# Access dataset information
dataset = syd.datasets[0]
print(f"Dataset: {dataset.name}")
print(f"From: {dataset.email}")
print(f"URL: {dataset.syft_url}")
```

### Interactive UI Features

The Jupyter interface provides:
- **Real-time search** - Filter datasets as you type
- **Checkbox selection** - Select multiple datasets visually
- **One-click code generation** - Automatically generates Python code
- **Automatic clipboard copy** - Generated code copied to clipboard
- **Responsive design** - Works on different screen sizes

## 🔧 API Reference

### DatasetCollection

The main interface for working with datasets:

```python
# Search and filter
syd.datasets.search("keyword")              # Search by name or email
syd.datasets.filter_by_email("@domain.com") # Filter by email pattern

# Access datasets
syd.datasets[0]                             # Get first dataset
syd.datasets[:5]                            # Get first 5 datasets
syd.datasets.get_by_indices([0, 2, 4])      # Get specific indices

# Utility methods
syd.datasets.list_unique_emails()           # List all unique emails
syd.datasets.list_unique_names()            # List all unique names
len(syd.datasets)                           # Count datasets
syd.datasets.help()                         # Show help message
```

### Dataset Object

Individual dataset representation:

```python
dataset = syd.datasets[0]

# Properties
dataset.name          # Dataset name
dataset.email         # Owner email
dataset.syft_url      # Full syft:// URL
dataset.dataset_obj   # Original SyftBox dataset object
```

## 🎨 Interactive Features

### Search and Filter

```python
# Search across names and emails
results = syd.datasets.search("financial")

# Filter by email domain
openmined_datasets = syd.datasets.filter_by_email("openmined.org")

# Chain operations
crop_data = syd.datasets.search("crop").filter_by_email("andrew")
```

### Selection Workflow

1. **Browse**: Use `syd.datasets` to see all available datasets
2. **Search**: Filter using the search box or programmatic methods
3. **Select**: Check boxes for datasets you want to use
4. **Generate**: Click "Generate Code" to create Python code
5. **Copy**: Code is automatically copied to clipboard

### Generated Code Examples

For single dataset:
```python
# Selected dataset:
dataset = syd.datasets[0]
```

For multiple datasets:
```python
# Selected datasets:
datasets = [syd.datasets[i] for i in [0, 1, 5]]
```

## 🔍 Advanced Usage

### Dataset Discovery

```python
# Check connection status
syd.datasets  # Shows connection status in output

# Get unique information
emails = syd.datasets.list_unique_emails()
names = syd.datasets.list_unique_names()
```

### Custom Workflows

```python
# Find datasets with specific patterns
ml_datasets = [
    ds for ds in syd.datasets 
    if any(keyword in ds.name.lower() for keyword in ['model', 'train', 'test'])
]

# Group by email domain
from collections import defaultdict
by_domain = defaultdict(list)
for ds in syd.datasets:
    domain = ds.email.split('@')[1]
    by_domain[domain].append(ds)
```

## 🛠️ Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/OpenMined/syft-datasets.git
cd syft-datasets

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=syft_datasets

# Run specific test file
pytest tests/test_datasets.py
```

### Code Quality

```bash
# Format code
ruff format

# Lint code
ruff check

# Type checking
mypy syft_datasets/
```

## 📚 Dependencies

- **syft-core** - Core SyftBox functionality
- **syft-rds** - Remote datasite session management
- **pandas** - Data manipulation and analysis
- **tabulate** - Text-based table formatting
- **requests** - HTTP library for status checks

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Ways to Contribute

- 🐛 **Bug Reports** - Report issues you encounter
- 💡 **Feature Requests** - Suggest new features
- 📝 **Documentation** - Improve or add documentation
- 🔧 **Code Contributions** - Submit pull requests

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [SyftBox](https://github.com/OpenMined/syftbox) - The main SyftBox platform
- [syft-core](https://github.com/OpenMined/syft-extras) - Core SyftBox utilities
- [syft-event](https://github.com/OpenMined/syft-extras) - Event handling for SyftBox
- [syft-rds](https://github.com/OpenMined/syft-rds) - Remote datasite sessions

## 💬 Community

- **Discord**: Join our [Discord community](https://discord.gg/openmined)
- **Twitter**: Follow [@OpenMinedOrg](https://twitter.com/OpenMinedOrg)
- **Blog**: Read our [blog](https://blog.openmined.org/)

---

**Made with ❤️ by the OpenMined community** 