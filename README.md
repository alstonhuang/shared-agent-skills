# Shared Agent Skills

This repository contains reusable skills for AI Agents (Google Antigravity/Deepmind).

## Available Skills

### 1. dual_layer_memory
Enables a persistent dual-layer (Short/Long term) memory system for the agent using local files.
- **Usage**: Load this skill to ensure context persistence across sessions.

### 2. command_center_reporter
Enables AI agents to report status to the central AI Command Center via GitHub API.
- **Usage**: Use this skill to automatically update project status in the Command Center dashboard.

## Installation
Clone this repository and symlink the desired skills to your agent's `.agent/skills` directory.

## 🕹️ Available Commands

When these skills are installed, you can use the following commands or prompts:

### 🧠 Dual Layer Memory
**Implicit Behavior**: This skill is **always on**. The agent will automatically check `memory/` folder at startup.

**Manual Triggers**:
- **"Initialize Memory"**: Forces the creation of `memory/SHORT_TERM.md` and `LONG_TERM.md` if they don't exist.
- **"Update Memory" or "Memorize"**: Forces the agent to explicitly write current progress to `SHORT_TERM.md`.
- **"Learn Rule: [Rule]"**: Explicitly adds a new rule to `LONG_TERM.md`.

### 📡 Command Center Reporter
**Slash Command**:
- `/cc-report`: Triggers the agent to summarize current session and report it to the central Command Center. (Alias: `/report`)

**Implicit Behavior**:
- The agent may proactively report major milestones (e.g., "Feature 'Login' is complete") if instructed to do so.
