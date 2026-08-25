# Contributing to AEONRIFT

Thank you for your interest in contributing to **AEONRIFT**! We welcome contributions from developers, researchers, and system architects.

## Code of Conduct

All contributors must adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before participating.

## How to Contribute

### 1. Reporting Issues
- Search existing issues before submitting a new bug report.
- Include OS version, Python/TypeScript versions, execution logs, and step-by-step reproduction steps.

### 2. Proposing Features & Research Enhancements
- For major architectural shifts (e.g., new checkpointing strategies, causal graph algorithms, or reconciliation policies), please open a Discussion or RFC issue first.

### 3. Pull Request Guidelines
- Branch naming convention: `feat/feature-name`, `fix/bug-name`, `docs/doc-update`.
- Ensure all tests pass: `pytest` for Python packages and `npm test` for TypeScript SDK.
- Maintain comprehensive unit test coverage for any newly introduced recovery logic or side-effect policies.
- Keep commits granular and clear.

## Development Setup

```bash
# Clone repository
git clone https://github.com/anshrajore/AEONRIFT-Time-travel-infrastructure-for-AI-agents.git
cd AEONRIFT-Time-travel-infrastructure-for-AI-agents

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install editable packages
pip install -e packages/core
pip install -e packages/runtime
pip install -e packages/cli
```
