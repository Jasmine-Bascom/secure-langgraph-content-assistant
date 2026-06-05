# Secure LangGraph Content Assistant

A LangGraph-based multi-agent content assistant that routes user requests to specialized agents for:

- SEO blog writing
- X/Twitter post writing
- General responses

The project demonstrates multi-agent routing, tool-calling loops, persistent conversation memory, and least-privilege tool access. Security-focused extensions will add prompt-injection checks, output validation, and adversarial test cases.

## Architecture

```text
User Input
   ↓
Router
   ↓
SEO Blog Writer / X Writer / General Handler
   ↓
Tool Loop if needed
   ↓
Final Response