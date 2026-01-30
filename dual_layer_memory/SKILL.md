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

3.  **Memory Writing Rules (CRITICAL)**:
    
    **Quality Standard**: Each memory entry must be **self-contained** and **actionable**.
    
    **❌ Too Brief (FORBIDDEN)**:
    ```markdown
    - Completed API integration
    - Fixed bug
    - Updated UI
    ```
    *Problem*: No context, can't resume work without finding old conversation.
    
    **❌ Too Verbose (FORBIDDEN)**:
    ```markdown
    - Integrated Yahoo Finance API by first installing the yahoo-finance2 package using npm install yahoo-finance2, then created a new API route at src/app/api/stock/[symbol]/route.ts which accepts a stock symbol as a parameter and returns the current price, change, and change percentage. The implementation uses the quoteSummary method from yahoo-finance2 with the 'price' module to fetch real-time data. Error handling was added to return 404 if the symbol is not found...
    ```
    *Problem*: Too much detail, wastes tokens, hard to scan.
    
    **✅ CORRECT Format**:
    ```markdown
    - Integrated Yahoo Finance API
      - Package: yahoo-finance2
      - Route: /api/stock/[symbol]
      - Returns: { price, change, changePercent }
      - Tested: AAPL, TSLA, NVDA ✅
      - Next: Add caching layer
    ```
    *Why*: Concise but complete. Includes what, how, status, and next steps.
    
    **Golden Rules**:
    - **3-5 bullet points** per major task
    - Include: **What** (task), **How** (key tech/approach), **Status** (done/blocked), **Next** (if incomplete)
    - Use **concrete names** (file paths, package names, API endpoints)
    - Avoid: "implemented feature", "fixed issue" (too vague)
    - Prefer: "implemented /api/portfolio route using Prisma aggregation"

4.  **Strict Rules**:
    - Do not rely on conversation history for critical project details if they are not in the memory files.
    - The memory files are the Single Source of Truth (SSOT).
    - **Privacy First**: The `memory/` folder MUST be git-ignored in the current workspace.

5.  **Cloud Sync (Replication)**:
    - **Objective**: Keep the local `memory/` folder in sync with the Private Data Repository.
    - **Mechanism**:
        - You cannot use `git push` directly on `memory/` because it is git-ignored locally.
        - Instead, you must use the **GitHub API** (via `python script` or similar) to fetch/update the contents of `memory/SHORT_TERM.md`, `memory/LONG_TERM.md`, and `memory/CONVERSATIONS.md` in the `PRIVATE_DATA_REPO`.
    - **Trigger**:
        - **Pull**: On Session Start (if memory is empty).
        - **Push**: On Session End (or Critical Milestone).
    - **Implementation**:
        - Use the `reporter_client.py` (which now supports file updates) or write a dedicated script to overwrite the remote memory files with local content.

6.  **CONVERSATIONS.md Structure**:
    ```markdown
    ### YYYY-MM-DD | "Conversation Title"
    - **Project**: ProjectName
    - **Focus**: Main topic/feature worked on
    - **Completed**: 2-3 key accomplishments
    - **Status**: 🟢 Active / ✅ Done / 🔴 Blocked
    - **Next**: What to do in next session (if applicable)
    ```
    
    **Rules**:
    - One entry per conversation
    - Keep entries under 5 lines
    - Update at session end via `/report`
    - Most recent conversations at the top

