# Security Policy

## Why this matters

Claude Code plugins can bundle executable code: hook scripts, `bin/` executables, and MCP servers. Plugins installed from this marketplace run locally on your machine with the same privileges as your Claude Code session. Please review plugin source before installing.

## Supported versions

This marketplace is a single rolling release on the `main` branch. Only the latest commit is maintained.

## Reporting a vulnerability

If you discover a security issue in a plugin or in the marketplace infrastructure itself:

1. **Do not open a public GitHub issue.**
2. Email **olivier@devbox.ch** with the subject `[SECURITY] ai-tools-marketplace`.
3. Include: affected plugin name, description of the issue, steps to reproduce, and potential impact.

You will receive an acknowledgement within 48 hours. I will work with you on a fix and coordinate disclosure.

## Scope

- Plugin hook scripts and executables that could enable privilege escalation or data exfiltration.
- MCP server configurations that expose sensitive environment variables.
- marketplace.json entries that point to malicious or typo-squatted sources.

Out of scope: general Claude Code vulnerabilities — report those to Anthropic directly.
