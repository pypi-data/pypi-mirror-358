# diagram-to-iac

> **"One container, many minds—zero manual toil."**

An automated DevOps-in-a-Box system that intelligently handles complete Repo-to-Deployment (R2D) workflows. The project combines AI-powered infrastructure analysis with GitHub automation for self-healing deployments.

## 🚀 DevOps-in-a-Box: R2D Action

The **R2D (Repo-to-Deployment) Action** is a self-healing, Terraform-first DevOps automation solution that lives inside a single GitHub Action. When you supply any repository URL, our SupervisorAgent marshals specialized agents to handle the complete deployment workflow.

### 🎯 2-Minute Quick Start

**Step 1:** Add the unified workflow to your repository:

```yaml
# .github/workflows/r2d-unified.yml
name: R2D - DevOps in a Box
on:
  issues:
    types: [opened, edited]
  pull_request:
    types: [closed]
  workflow_dispatch:
    inputs:
      repo_url:
        description: 'Repository URL to deploy'
        required: false
        type: string

jobs:
  r2d-deploy:
    uses: amartyamandal/diagram-to-iac/.github/workflows/r2d-unified.yml@main
    secrets: inherit
    with:
      repo_url: ${{ inputs.repo_url || github.server_url }}/${{ github.repository }}
```

**Step 2:** Configure your secrets (see [complete guide](docs/R2D_USER_GUIDE.md))

**Step 3:** Trigger deployment via issue, PR merge, or manual run

> 📚 **[Complete Setup Guide](docs/R2D_USER_GUIDE.md)** - Everything you need in one place!

### Key Features

- **🤖 Self-Healing**: Automatically creates GitHub Issues for errors and suggests fixes
- **🔒 Security-First**: Non-root container execution with workspace isolation
- **🌍 Multi-Cloud**: Supports Terraform, PowerShell, Bash, and Ansible deployments
- **📊 Observable**: Rich logging, step summaries, and artifact collection
- **🔄 Resumable**: Thread-based conversation tracking for workflow continuation
- **🧪 Testable**: Comprehensive dry-run mode for safe testing

### The Cast: Specialized Agents

| Agent | Capability | Never Does |
|-------|------------|------------|
| **SupervisorAgent** | Orchestrates workflow, manages checkpoints | Edit code directly |
| **GitAgent** | Clone, branch, PR creation, assign @github-copilot | Guess network credentials |
| **ShellAgent** | Safe command execution, stack detection | Execute non-allowlisted binaries |
| **TerraformAgent** | Init/plan/apply, error classification | Apply with critical security issues |
| **PolicyAgent** | tfsec + OPA security gates | Ignore critical findings |

## 📦 Installation

Create a virtual environment with Python 3.11+ and install the project in editable mode. Development dependencies (linting, testing, etc.) are provided through the `dev` extra:

```bash
pip install -e .[dev]
```

## 🖥️ Running the CLI

The project exposes several entry points via `pyproject.toml`:

### Main R2D CLI
```bash
# Run complete R2D workflow
diagram-to-iac https://github.com/user/repo
r2d-agent https://github.com/user/repo --dry-run

# Get help
diagram-to-iac --help
```

### Individual Agent CLIs
```bash
# SupervisorAgent (orchestration)
supervisor-agent --repo-url https://github.com/user/repo

# GitAgent (repository operations)
git-agent --repo-url https://github.com/user/repo

# TerraformAgent (infrastructure deployment)
terraform-agent --query "terraform plan"
```

### Interactive Mode

Running without arguments enters interactive mode:

```bash
$ supervisor-agent --dry-run
╔══════════════════════════════════════════════════════════════════════════════╗
║  🤖 DevOps-in-a-Box: SupervisorAgent                                        ║
║  "One container, many minds—zero manual toil."                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Repository URL: https://github.com/octocat/Hello-World.git
🚀 R2D SupervisorAgent - Workflow Orchestration
📅 Default branch name: r2d-<timestamp>
📝 Press Enter to use default, or type a custom branch name:
```

The agent will continue with the complete workflow (clone → detect → deploy → issue creation). The `--dry-run` flag simulates actions without making changes.

## Running Tests

All tests use `pytest` and are located under the `tests` directory. After installing the development dependencies, run:

```bash
pytest
```

## 📊 Logs and Observability

DevOps-in-a-Box provides comprehensive observability for all R2D workflows:

### Structured Logging
Each run creates a JSONL log file under the `logs/` directory (e.g. `logs/run-<timestamp>.jsonl`).
Every significant event is logged as structured JSON for easy parsing and analysis:

```bash
# Follow live logs
tail -f logs/run-*.jsonl

# Parse with jq for specific events
cat logs/run-*.jsonl | jq '. | select(.event_type == "terraform_apply")'
```

### Step Summary Dashboard
After each workflow, a Markdown dashboard is generated at `step-summary.md` with:
- 📈 Terraform resource changes and cost estimates
- 🔒 Security findings from tfsec/OPA scans
- 🏗️ Infrastructure modules and dependencies
- ⚡ Performance metrics and execution times

### GitHub Integration
- **Issues**: Automatically created for errors with detailed context
- **Pull Requests**: Auto-drafted fixes assigned to @github-copilot
- **Workflow Summaries**: Rich GitHub Actions step summaries
- **Artifacts**: Logs, plans, and reports uploaded for download

### CI/CD Artifacts
In GitHub Actions, the following artifacts are automatically collected:
- `logs/` - Structured JSONL logs
- `*.tfplan` - Terraform plan files  
- `step-summary.md` - Workflow dashboard
- `r2d-artifacts/` - Complete workflow artifacts

## 🔧 GitHub Actions Usage

The R2D system now uses a **unified workflow** that handles all deployment scenarios automatically. This replaces the previous multiple workflow files with a single, intelligent solution.

### ⚡ Simple Setup (Recommended)

Add this single workflow file to get all R2D capabilities:

```yaml
# .github/workflows/r2d-unified.yml
name: R2D - DevOps in a Box
on:
  issues:
    types: [opened, edited]
  pull_request:
    types: [closed]
  workflow_dispatch:
    inputs:
      repo_url:
        description: 'Repository URL to deploy'
        required: false
        type: string

jobs:
  r2d-deploy:
    uses: amartyamandal/diagram-to-iac/.github/workflows/r2d-unified.yml@main
    secrets: inherit
    with:
      repo_url: ${{ inputs.repo_url || github.server_url }}/${{ github.repository }}
```

### 🎮 Multiple Ways to Deploy

- **📝 Issue-based**: Create an issue with "deploy" in title/body
- **🔀 PR merge**: Automatic deployment when PRs are merged
- **🎯 Manual**: Use workflow_dispatch with optional custom repo URL
- **🔒 External repos**: Deploy any accessible repository

### 📋 Required Secrets

Configure these in your repository settings → Secrets and variables → Actions:

| Secret | Description | Required |
|--------|-------------|----------|
| `GITHUB_TOKEN` | GitHub API access (auto-provided) | ✅ Yes |
| `TF_CLOUD_TOKEN` | Terraform Cloud workspace token | ✅ Yes |
| `OPENAI_API_KEY` | OpenAI API key for AI features | ❌ Optional |
| `ANTHROPIC_API_KEY` | Claude API key for AI features | ❌ Optional |
| `DOCKERHUB_USERNAME` | DockerHub username for private containers | ❌ Optional |
| `DOCKERHUB_TOKEN` | DockerHub access token for private containers | ❌ Optional |

> 📚 **[Complete Setup Guide](docs/R2D_USER_GUIDE.md)** includes examples, troubleshooting, and advanced configurations.
> 
> **Note**: The system automatically maps `TF_CLOUD_TOKEN` to the internal `TFE_TOKEN` environment variable.
> **DockerHub**: Only needed if using private container registries.

## 📈 Observability & Monitoring

After each workflow run, comprehensive artifacts are generated:

- **📊 Step Summary Dashboard**: `step-summary.md` with Terraform changes, security findings, and metrics
- **📋 Structured Logs**: JSONL format in `logs/` directory for analysis  
- **🔍 GitHub Integration**: Automatic issue creation and PR suggestions
- **📦 Artifacts**: Plans, reports, and logs uploaded as GitHub Actions artifacts

## 🧪 Development & Testing

For local development and testing:

```bash
# Install development dependencies
pip install -e .[dev]

# Run the CLI locally
diagram-to-iac https://github.com/user/repo --dry-run

# Run tests
pytest
```

## 📚 Documentation

**🎯 [THE ONLY GUIDE YOU NEED: Definitive Integration Guide](docs/DEFINITIVE_INTEGRATION_GUIDE.md)**

*All other documentation is for reference only. Start with the guide above.*

### Reference Documentation
- [Working Examples](docs/WORKING_EXAMPLES.md) - Copy-paste examples that work immediately
- [R2D User Guide](docs/R2D_USER_GUIDE.md) - Complete setup and usage guide
- [Migration Guide](docs/MIGRATION_GUIDE.md) - Migrate from old workflows to unified approach
- [Container Action](.github/actions/r2d/) - Technical details of the container action
- [Agent Architecture](src/diagram_to_iac/agents/) - How the AI agents work together
- [Simplification Summary](docs/SIMPLIFICATION_COMPLETION_SUMMARY.md) - What changed in the unified approach

## 🤝 Contributing

This project follows strict coding standards and security practices. See the development guidelines in the repository for contribution instructions.

---

> **"One container, many minds—zero manual toil."** 🤖
