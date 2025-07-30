# 🤖 DevOps-in-a-Box: R2D Action

> **"One container, many minds—zero manual toil."**

The **R2D (Repo-to-Deployment) Action** is a self-healing, Terraform-first DevOps automation solution. Simply add one workflow file to your repository, and our AI-powered SupervisorAgent handles the complete deployment pipeline.

## ⚡ Quick Start (2 minutes)

### 1. Add the Workflow

Create `.github/workflows/r2d.yml` in your repository:

```yaml
name: "Deploy Infrastructure"

on:
  # Deploy when issues are labeled
  issues:
    types: [opened, labeled]
  
  # Deploy when PRs merge to main
  pull_request:
    types: [closed]
  
  # Manual deployment control
  workflow_dispatch:

jobs:
  deploy:
    uses: amartyamandal/diagram-to-iac/.github/workflows/r2d-unified.yml@v1
    secrets:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      TF_CLOUD_TOKEN: ${{ secrets.TF_CLOUD_TOKEN }}
```

### 2. Configure Secrets

Add these to your repository secrets (`Settings` → `Secrets and variables` → `Actions`):

| Secret | Description | Required |
|--------|-------------|----------|
| `TF_CLOUD_TOKEN` | [Terraform Cloud API Token](https://app.terraform.io/app/settings/tokens) (**base64 encoded**) | ✅ **Required** |
| `OPENAI_API_KEY` | OpenAI API key for enhanced AI features (**base64 encoded**) | ❌ Optional |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key (**base64 encoded**) | ❌ Optional |

> **🚨 CRITICAL**: All secret values must be **base64-encoded** before adding to GitHub.
> 
> **Note**: `GITHUB_TOKEN` is automatically provided by GitHub Actions.
> 
> **Important**: The system internally maps `TF_CLOUD_TOKEN` to the expected `TFE_TOKEN` environment variable.

#### Base64 Encoding Your Secrets
```bash
# Encode your secrets before adding to GitHub
echo -n "your-tf-cloud-token" | base64
echo -n "your-openai-api-key" | base64
```

### 3. Deploy! 

Choose your deployment method:

**🏷️ Issue-Based Deployment** (Recommended)
1. Create an issue in your repository
2. Add the label `r2d-request` 
3. Watch the magic happen! ✨

**🔀 PR-Based Deployment** 
- Merge any PR to your main branch
- Automatic deployment triggers

**🎮 Manual Deployment**
- Go to `Actions` → `Deploy Infrastructure` → `Run workflow`

## 🎯 What It Does

When triggered, the R2D Action:

1. **🔍 Analyzes** your repository (Terraform, Ansible, PowerShell, Bash)
2. **🔐 Validates** all secrets and dependencies upfront  
3. **🏗️ Deploys** infrastructure via Terraform Cloud
4. **🤖 Auto-fixes** common issues with Pull Requests
5. **📋 Creates** GitHub Issues for complex problems (assigned to @github-copilot)
6. **📊 Provides** rich summaries and observability

Everything happens in **one umbrella issue** per deployment, so you get a clean narrative instead of workflow noise.

## 🛠️ Advanced Configuration

### 🔧 Environment Variable Mapping

**Important**: The unified workflow automatically handles environment variable mapping:

| Secret Name (Repository) | Environment Variable (Internal) | Purpose |
|---------------------------|----------------------------------|---------|
| `TF_CLOUD_TOKEN` | `TFE_TOKEN` | Terraform Cloud API access |
| `GITHUB_TOKEN` | `GITHUB_TOKEN` | GitHub API access |
| `OPENAI_API_KEY` | `OPENAI_API_KEY` | OpenAI API access |
| `ANTHROPIC_API_KEY` | `ANTHROPIC_API_KEY` | Anthropic API access |

You set `TF_CLOUD_TOKEN` as a repository secret, and the system automatically maps it to the `TFE_TOKEN` environment variable that the agents expect.

### Custom Trigger Labels

```yaml
jobs:
  deploy:
    uses: amartyamandal/diagram-to-iac/.github/workflows/r2d-unified.yml@v1
    with:
      trigger_label: 'deploy-prod'  # Custom label instead of 'r2d-request'
    secrets:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      TF_CLOUD_TOKEN: ${{ secrets.TF_CLOUD_TOKEN }}
```

### Multi-Environment Setup

```yaml
name: "Multi-Environment Deployment"

on:
  issues:
    types: [labeled]

jobs:
  deploy-dev:
    if: contains(github.event.issue.labels.*.name, 'deploy-dev')
    uses: amartyamandal/diagram-to-iac/.github/workflows/r2d-unified.yml@v1
    with:
      target_branch: 'develop'
    secrets:
      TF_CLOUD_TOKEN: ${{ secrets.TF_CLOUD_TOKEN_DEV }}
      
  deploy-prod:
    if: contains(github.event.issue.labels.*.name, 'deploy-prod')
    uses: amartyamandal/diagram-to-iac/.github/workflows/r2d-unified.yml@v1
    with:
      target_branch: 'main'
    secrets:
      TF_CLOUD_TOKEN: ${{ secrets.TF_CLOUD_TOKEN_PROD }}
```

### External Repository Deployment

```yaml
jobs:
  deploy:
    uses: amartyamandal/diagram-to-iac/.github/workflows/r2d-unified.yml@v1
    with:
      repo_url: 'https://github.com/my-org/infrastructure-repo'
    secrets:
      GITHUB_TOKEN: ${{ secrets.INFRASTRUCTURE_REPO_TOKEN }}
      TF_CLOUD_TOKEN: ${{ secrets.TF_CLOUD_TOKEN }}
```

## 🔒 Security & Permissions

The R2D Action follows security best practices:

- **🏠 Isolated Execution**: Runs in dedicated containers with minimal privileges
- **🔐 Secret Safety**: Never logs or exposes secrets
- **👥 Access Control**: Only repository members/collaborators can trigger deployments
- **🛡️ Security Scanning**: Built-in tfsec and OPA policy enforcement
- **📋 Audit Trail**: Complete logging and artifact collection

### Required Permissions

The workflow needs these permissions (automatically handled):

```yaml
permissions:
  contents: read        # Read repository code
  issues: write         # Create/update issues for error tracking
  pull-requests: write  # Create auto-fix PRs
```

## 🎭 The AI Agent Team

Your deployment is handled by specialized AI agents:

| Agent | Superpower | Never Does |
|-------|------------|------------|
| **🧠 SupervisorAgent** | Orchestrates workflow, manages checkpoints | Edit your code directly |
| **📂 GitAgent** | Clone, branch, PR creation, assign @github-copilot | Guess credentials |
| **🖥️ ShellAgent** | Safe command execution, stack detection | Execute unauthorized binaries |
| **🏗️ TerraformAgent** | Init/plan/apply, error classification | Apply with critical security issues |
| **🛡️ PolicyAgent** | Security scanning with tfsec + OPA | Ignore critical findings |

## 📊 Observability

Every deployment provides rich observability:

### 📋 Issue Tracking
- One "umbrella issue" per deployment with full narrative
- Real-time status updates and progress tracking
- Automatic error escalation and resolution suggestions

### 📈 Workflow Summaries  
- Terraform resource changes and cost estimates
- Security findings from policy scans
- Performance metrics and execution times
- Artifact collection (logs, plans, reports)

### 🔍 Debugging
All deployment artifacts are automatically collected:
- Structured JSONL logs
- Terraform plan files
- Security scan reports  
- Complete workflow dashboard

## 🆘 Troubleshooting

### Common Issues

**❌ "Missing TF_CLOUD_TOKEN"**
- Add your Terraform Cloud API token to repository secrets
- Get it from: https://app.terraform.io/app/settings/tokens

**❌ "Workflow not triggering"**
- Ensure issue author is a repository member/collaborator  
- Check that the correct label (`r2d-request`) is applied
- Verify workflow file is in `.github/workflows/` directory

**❌ "Permission denied"**
- Repository must have `issues: write` and `pull-requests: write`
- User must be member/collaborator (not external contributor)

### Getting Help

1. **📋 Check the umbrella issue** created by the deployment
2. **📂 Download workflow artifacts** from the Actions run
3. **🏷️ Create an issue** with label `r2d-support` for assistance

## 🚀 Examples

### Basic Infrastructure Repository

Repository structure:
```
my-infrastructure/
├── .github/workflows/r2d.yml    # R2D workflow
├── main.tf                      # Terraform configuration
├── variables.tf
└── outputs.tf
```

Deployment process:
1. Create issue: "Deploy database infrastructure"
2. Add label: `r2d-request`
3. R2D automatically deploys via Terraform Cloud
4. Success summary posted in issue

### Multi-Module Terraform

```
complex-infrastructure/
├── .github/workflows/r2d.yml
├── modules/
│   ├── networking/
│   ├── compute/
│   └── storage/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
└── policies/
    └── security.rego
```

R2D handles:
- Dependency resolution between modules
- Environment-specific configurations  
- Security policy enforcement
- Cost estimation and approval workflows

## 📚 Additional Resources

- **[Full Documentation](https://github.com/amartyamandal/diagram-to-iac/blob/main/README.md)**
- **[Security Best Practices](https://github.com/amartyamandal/diagram-to-iac/blob/main/docs/SECURITY.md)**
- **[Example Workflows](https://github.com/amartyamandal/diagram-to-iac/tree/main/.github/workflows)**
- **[Troubleshooting Guide](https://github.com/amartyamandal/diagram-to-iac/blob/main/docs/TROUBLESHOOTING.md)**

---

**DevOps-in-a-Box**: Bringing enterprise-grade DevOps automation to every repository. 🤖✨
