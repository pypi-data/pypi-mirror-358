# Lykos - Git Secret Guardian

<p align="center">
  <img src="lykos/assets/lykos.png" alt="lykos Logo" width="400"/>
</p>

A comprehensive Python toolkit for detecting, removing, and preventing secrets in Git repositories. This suite combines scanning, history cleaning, and protection mechanisms to secure your codebase.

## Quick Start

```bash
pip install -r requirements.txt

# full protection workflow
lykos protect --confidence HIGH

lykos scan --all --confidence MEDIUM
```

## TLDR - Essential Commands
```bash
lykos scan --all --confidence HIGH
lykos scan --recent 50 --confidence MEDIUM # last 50 commits

# this will install a hook 
lykos guard --install --confidence HIGH

# clean secrets manually from history
lykos clean --confidence HIGH
lykos clean --scope all --confidence MEDIUM

Example: lykos clean --replace "AIzaSyMaps567890abcdefghijklmnopqrstuv==REDACTED_OPENAI_KEY" ## this will replace whatever secrets you have with REDACTED_OPENAI_KEY

# full workflow
lykos protect --confidence HIGH

lykos guard --check-files *.py --confidence HIGH
lykos guard --check-staged --confidence HIGH

lykos status 
```

## Commands Overview

| Command | Purpose |
|---------|---------|
| `lykos scan` | Scan git history for potential or known secrets |
| `lykos guard` | Install pre-commit hooks to prevent secrets from going into your git|
| `lykos clean` | Removes secrets from git history |
| `lykos protect` | Complete workflow: scan, clean, and setup protection |

## Command Usage

### 1. Scanning (`lykos scan`)

Scan git history for potential secrets using patterns and entropy analysis.

```bash
lykos scan --all --confidence MEDIUM

# last 50 commits on current branch
lykos scan --recent 50 --confidence HIGH

# scan specific branch without switching
lykos scan --branch main --confidence HIGH

# custom output file and entropy threshold
lykos scan --all --output my_secrets.json --entropy 5.0 --confidence LOW

# Save report instead of interactive mode
lykos scan --recent 100 --save-report --confidence MEDIUM
```

**Tip**: If you omit --all, --branch, and --recent, lykos already scopes the scan to the current branch by default. So a plain:

**Features:**
- Pattern matching for AWS, Google, GitHub, OpenAI, Stripe keys
- Shannon entropy detection for generic high-entropy strings
- Confidence scoring system (HIGH/MEDIUM/LOW/VERY_LOW)
- Interactive cleaning workflow
- JSON report generation

### 2. Pre-commit Protection (`lykos guard`)

Prevent secrets from being committed in the first place.

```bash
lykos guard --install --confidence HIGH

lykos guard --check-staged --confidence MEDIUM

# Check specific files
lykos guard --check-files file1.py file2.py --confidence HIGH

# Check entire directory
lykos guard --check-dir src/ --confidence MEDIUM

# Strict mode (blocks commits for any violation)
lykos guard --check-staged --strict --confidence LOW
```

**Features:**
- Automatic git hook installation
- Configurable confidence thresholds

### 3. History Cleaning (`lykos clean`)

Remove secrets from git history using git-filter-repo.

```bash
# clean secrets from currently-checked-out files
lykos clean --confidence MEDIUM

# Clean from all branches
lykos clean --scope all --confidence HIGH

# you can do manual replacements if lykos fails to flag it out
lykos clean --replace "old_secret==NEW_SECRET" --confidence HIGH

# multiple manual replacements
lykos clean --replace "secret1==REDACTED" --replace "secret2==REDACTED" --confidence MEDIUM
```

**Features:**
- Auto backup branch creation
- Integration with scanner confidence scores
- Able to do manual replacement

### 4. Complete Protection (`lykos protect`)

Full workflow: scan for secrets, clean history, and setup protection.

```bash
# complete protection workflow with HIGH confidence
lykos protect --confidence HIGH

# Protect recent commits only
lykos protect --recent 100 --confidence MEDIUM

# Dry run to see what would be done
lykos protect --dry-run --confidence HIGH

# Custom report file
lykos protect --report my_custom_report.json --confidence MEDIUM
```

## Quick Workflows

### Emergency: "I just committed a secret!"

```bash
# Quick scan and clean recent commits
lykos protect --recent 10 --confidence HIGH

# Then immediately:
# 1. Revoke the exposed key
# 2. Force push: git push --force-with-lease
# 3. Notify team to re-clone
```

### Secure New Repository

```bash
# Setup protection for new repo
lykos guard --install --confidence HIGH
```

### Check Repository Status

```bash
# Get security status overview
lykos status
```

## Config

### Confidence Levels

Choose the appropriate confidence level for your security needs:

- **HIGH** (0.8+): Only very likely real secrets (recommended for production)
- **MEDIUM** (0.5+): Probable secrets with some false positives (good default)
- **LOW** (0.2+): Includes more potential secrets (higher false positive rate)
- **VERY_LOW** (0.05+): Maximum sensitivity (many false positives)

```bash
# High security - only block/clean obvious secrets
lykos guard --install --confidence HIGH
lykos clean --scope working --confidence HIGH ## rewrite current files
lykos clean --scope history --confidence MEDIUM ## rewrite full history

# Balanced approach - good for most teams
lykos protect --confidence MEDIUM

# Maximum sensitivity - catches everything
lykos scan --all --confidence VERY_LOW
```

### Entropy Threshold

Adjust sensitivity for high-entropy detection:

```bash
# More sensitive (lower threshold)
lykos scan --all --entropy 4.0 --confidence MEDIUM

# Less sensitive (higher threshold)  
lykos scan --all --entropy 5.5 --confidence MEDIUM
```

### False Positives

Add known false positives to `.secretsignore`:

```bash
# Create .secretsignore file
echo "YOUR_CUSTOM_TEST_KEY" >> .secretsignore
echo "EXAMPLE_TOKEN_12345" >> .secretsignore
```

## Security Best Practices

### After Finding Secrets:

1. **IMMEDIATELY** revoke/regenerate the exposed keys
2. Clean git history: `lykos clean --confidence HIGH`
3. Force push the cleaned history: `git push --force-with-lease`
4. Check access logs for unauthorized usage
5. Notify team members to re-clone the repository
6. Update applications using the compromised keys

### Prevention:

1. Install pre-commit hooks: `lykos guard --install --confidence HIGH`
2. Use environment variables for secrets
3. Use secret management services (AWS Secrets Manager, HashiCorp Vault)
4. Regular security audits: `lykos scan --all --confidence MEDIUM`
5. Team training on secure coding practices

## Detection Capabilities

### Pattern-Based Detection:
- AWS Access Keys (`AKIA...`)
- AWS Secret Keys (40-char base64)
- Google API Keys (`AIza...`)
- GitHub Tokens (`ghp_...`)
- OpenAI API Keys (`sk-...`)
- Anthropic API Keys (`sk-ant-...`)
- Stripe Keys (`sk_live_...`, `sk_test_...`)
- JWT Tokens (`eyJ...`)
- Private Keys (`-----BEGIN...`)
- Generic API Keys (pattern-based)
- Bearer Tokens

### Entropy-Based Detection:
- High-entropy strings that look random
- Configurable threshold (default: 4.5)
- Excludes common false positives
- Smart filtering for timestamps and IDs

### Confidence Scoring:
- **HIGH**: Very likely real secrets (AWS keys, GitHub tokens, etc.)
- **MEDIUM**: Probable secrets with good patterns
- **LOW**: Possible secrets, may include false positives
- **VERY_LOW**: Maximum sensitivity, many false positives

## Important

### !!! Git History Rewriting !!!:
- **Creates backup branches automatically**
- **Changes commit hashes** - coordinate with team
- **Requires force push** after cleaning
- **Team needs to re-clone** after history rewrite

### Dependencies:
- Requires `git-filter-repo` for history cleaning: `pip install git-filter-repo`
- Python 3.9+ required
- Git repository required for most operations

### Performance:
- Full repository scans can be slow on large repos
- Use `--recent N` for faster scans during development
- Pre-commit hooks add minimal overhead

## Exit Codes

lykos uses exit codes:

- **0**: Success, no secrets found
- **1**: Warnings or low-confidence secrets found
- **2**: High-confidence secrets found (action required)

## License

This toolkit is designed for security purposes. Use responsibly and in accordance with your organization's security policies.