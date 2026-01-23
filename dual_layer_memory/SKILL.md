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

2.  **Workflow Loop (Lazy Loading)**:
    - **Recall (Only when needed)**:
        - DO NOT read memory files on every turn.
        - Read `memory/SHORT_TERM.md` ONLY if:
            1. It is the very first turn of the conversation.
            2. The user asks for a status update.
            3. You are unsure about the current task or context.
    - **Execute**: Perform the user's request.
    - **Memorize (Batch Updates)**:
        - DO NOT update `SHORT_TERM.md` for minor steps.
        - Update `SHORT_TERM.md` ONLY when:
            1. A major task is completed.
            2. The session is about to end (user says "done", "bye", etc.).
            3. A critical decision or new rule is established.

3.  **Strict Rules**:
    - Do not rely on conversation history for critical project details if they are not in the memory files.
    - The memory files are the Single Source of Truth (SSOT).
