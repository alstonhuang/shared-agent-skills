---
name: dual_layer_memory
description: Enables a persistent dual-layer (Short/Long term) memory system for the agent using local files.
---
# Dual-Layer Memory System

## Description
This skill forces the agent to utilize a file-based memory system (`memory/SHORT_TERM.md` and `memory/LONG_TERM.md`) instead of relying solely on the context window. This ensures context persistence across sessions.

## Instructions
1.  **Check for Memory Files**:
    - At the start of the session, check if `memory/SHORT_TERM.md` and `memory/LONG_TERM.md` exist in the root of the workspace.
    - If they do not exist, create them.
      - `LONG_TERM.md`: Initialize with `# Project Long Term Memory\n\n- [Rule] Always use modular code.`
      - `SHORT_TERM.md`: Initialize with `# Current Session\n\n- Status: Initialized`

2.  **Workflow Loop**:
    - **Recall**: Before executing any task, read `memory/SHORT_TERM.md` (for immediate context) and `memory/LONG_TERM.md` (for rules/facts).
    - **Execute**: Perform the user's request.
    - **Memorize**: After the task (or significant step), UPDATE `memory/SHORT_TERM.md` with the new status, current task, and next steps.

3.  **Strict Rules**:
    - Do not rely on conversation history for critical project details if they are not in the memory files.
    - The memory files are the Single Source of Truth (SSOT).
