# Secure LangGraph Content Assistant

A security-focused LangGraph multi-agent content assistant that demonstrates both secure AI application design and modern DevSecOps practices.

This project routes user requests to specialized agents while applying layered security controls including prompt injection mitigation, moderation, PII redaction, output validation, audit logging, and automated CI/CD security scanning.

Originally developed as a multi-agent systems assignment, the project has evolved into a portfolio-ready demonstration of secure AI engineering, application security, and DevSecOps automation.

---

# Overview

The assistant routes user requests to one of three specialized agents:

- **SEO Blog Writer** — creates long-form, structured, keyword-aware blog content.
- **X/Twitter Writer** — creates concise social media posts under platform constraints.
- **General Handler** — answers general questions and supports conversational memory.

The project demonstrates:

- LangGraph multi-agent orchestration
- Secure routing and fallback behavior
- Least-privilege tool access
- Prompt injection mitigation
- Tool manipulation prevention
- OpenAI moderation integration
- Presidio PII detection and redaction
- Secret-like output detection
- Structured audit logging
- Conversation memory
- Automated behavioral testing
- GitHub Actions DevSecOps pipeline
- AI-assisted security review

---

# Architecture

```text
                     User Input
                          │
                          ▼
                Security Pre-Check
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
 Prompt Injection     Moderation     PII Redaction
                          │
                          ▼
                     LangGraph Router
                          │
      ┌───────────────────┼───────────────────┐
      ▼                   ▼                   ▼
 SEO Blog Writer     X/Twitter Writer     General Handler
      │                   │                   │
      └───────────────┬───┴───────────────────┘
                      ▼
              Tool Execution (if needed)
                      ▼
              Output Validation Layer
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
 Secret Detection   Moderation    PII Validation
                      │
                      ▼
               Structured Audit Log
                      │
                      ▼
                 Final Response
```

---

# DevSecOps Pipeline

This project includes a GitHub Actions DevSecOps workflow that automatically analyzes every push and pull request.

```text
Developer Push / Pull Request
              │
              ▼
        GitHub Actions
              │
              ├── pytest
              ├── Bandit
              ├── Semgrep
              ├── Gitleaks
              ├── pip-audit
              ▼
      AI Security Review
              ▼
     Markdown Security Report
              ▼
   GitHub Actions Job Summary
              ▼
 Workflow Artifacts
```

## Pipeline Components

### Unit Testing

`pytest` validates application functionality before security analysis begins.

### Bandit

Performs Python Static Application Security Testing (SAST) to detect issues including:

- insecure subprocess usage
- weak cryptography
- unsafe deserialization
- hardcoded credentials

### Semgrep

Provides broader rule-based static analysis for:

- injection vulnerabilities
- authentication issues
- insecure API usage
- framework-specific security problems

### Gitleaks

Scans commits and repository contents for:

- API keys
- passwords
- AWS credentials
- access tokens
- accidentally committed secrets

### pip-audit

Performs Software Composition Analysis (SCA) by checking project dependencies against known vulnerability databases.

### AI-Assisted Security Review

After deterministic scanners complete, an LLM analyzes:

- Pull request or push diff
- Bandit results
- Semgrep findings
- Gitleaks report
- Dependency vulnerabilities

It produces:

- Executive summary
- Prioritized findings
- Risk assessment
- Recommended remediation
- Manual review recommendations

The AI reviewer is intentionally **advisory only**. Deterministic scanners remain the source of truth for vulnerability detection.

---

# Secure AI Design

The AI reviewer follows several security principles.

## Least Privilege

The GitHub Actions workflow uses read-only repository permissions.

The AI cannot:

- merge code
- approve pull requests
- modify repositories
- deploy software

## Prompt Injection Resistance

Repository contents are treated as **untrusted input**.

The prompt explicitly instructs the model to ignore instructions contained within:

- source code
- comments
- commit messages
- scanner output
- documentation

## Human-in-the-Loop

Traditional security scanners remain authoritative.

The AI serves only as:

- summarizer
- prioritizer
- explainer

Human reviewers remain responsible for security decisions.

---

# Security Features

## Multi-Agent Routing

Requests are routed to one of three specialized agents:

- SEO Blog Writer
- X/Twitter Writer
- General Handler

Invalid routes automatically fall back to the general handler.

## Least-Privilege Tool Access

Each agent receives only the tools it requires.

| Agent | Purpose | Tool Access |
|-------|---------|-------------|
| SEO Writer | Long-form content | Research tools |
| X Writer | Social posts | Search tools |
| General | General conversation | No external tools |

## Prompt Injection Protection

The application detects common attacks including:

- Ignore previous instructions
- Reveal your system prompt
- Call this tool
- You are now the router
- Bypass your safety rules

## Moderation

OpenAI Moderation checks are performed on both:

- user input
- generated output

## PII Redaction

Presidio detects and anonymizes personally identifiable information before it reaches the model.

## Output Validation

Generated responses are checked for:

- secret-like strings
- moderation violations
- PII
- formatting requirements

## Structured Audit Logging

Security events are written as structured JSONL logs including:

- prompt injection attempts
- moderation events
- PII redaction
- validation failures
- successful validation

---

# Testing

The project uses **pytest** for behavioral testing.

Coverage includes:

- router behavior
- agent selection
- state transitions
- tool access
- security pre-checks
- prompt validation
- output validation
- audit logging
- PII handling

---

## Project Structure

```text
secure-langgraph-content-assistant/
├── .github/
│   └── workflows/
│       └── security-review.yml
├── notebooks/
│   └── assignment_template_multi_agents_systems.ipynb
├── scripts/
│   └── ai_security_review.py
├── src/
│   ├── __init__.py
│   ├── agents.py
│   ├── app.py
│   ├── audit.py
│   ├── graph.py
│   ├── model.py
│   ├── moderation.py
│   ├── pii.py
│   ├── prompts.py
│   ├── router.py
│   ├── security.py
│   ├── state.py
│   └── tools.py
├── tests/
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_audit.py
│   ├── test_pii.py
│   ├── test_router.py
│   ├── test_security.py
│   ├── test_state.py
│   └── test_tools.py
├── logs/
│   └── audit.jsonl (generated at runtime)
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── requirements-security.txt
```

---

# Setup

```bash
python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip

pip install -r requirements.txt
pip install -r requirements-security.txt
```

Copy the environment template:

```bash
cp .env.example .env
```

Add your API key:

```text
OPENAI_API_KEY=your_key_here
```

---

# Running the Application

```bash
python -m src.app
```

Run tests:

```bash
pytest
```

---

# CI/CD

The GitHub Actions workflow runs automatically on:

- Pushes
- Pull Requests
- Manual workflow dispatches

The workflow:

- Runs unit tests
- Executes Bandit
- Executes Semgrep
- Runs Gitleaks
- Performs dependency scanning
- Generates an AI-assisted security review
- Uploads reports as workflow artifacts
- Publishes a GitHub Actions job summary

---

# Why This Project

This project demonstrates how AI applications can be engineered with security as a first-class concern.

Rather than relying on a single defense, it layers multiple controls:

- Secure routing
- Prompt injection mitigation
- Least privilege
- Moderation
- PII protection
- Audit logging
- Automated testing
- DevSecOps automation
- AI-assisted security review

The result is a realistic demonstration of secure AI engineering and modern application security practices.

---

# Current Limitations

This project is intended as a portfolio demonstration rather than a production deployment.

Current limitations include:

- regex-based prompt injection detection
- simplified mock tools
- local audit logging
- advisory AI review
- no authentication or authorization
- no Infrastructure-as-Code scanning
- no container image scanning

---

# Future Improvements

Potential enhancements include:

- Checkov Infrastructure-as-Code scanning
- Trivy container scanning
- SBOM generation
- Cosign artifact signing
- GitHub Code Scanning (SARIF)
- automated pull request comments
- security metrics dashboard
- centralized logging
- richer adversarial testing
- FastAPI deployment
- Streamlit UI

---

# Skills Demonstrated

- Python
- LangGraph
- Multi-agent orchestration
- Prompt engineering
- AI security
- Prompt injection mitigation
- OpenAI Moderation API
- Presidio
- GitHub Actions
- CI/CD
- DevSecOps
- Application Security
- Static Application Security Testing (Bandit, Semgrep)
- Software Composition Analysis (pip-audit)
- Secret scanning (Gitleaks)
- AI-assisted security engineering
- Secure SDLC
- Security automation
- Structured audit logging