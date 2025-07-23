You need a "playbook" for managing your AI coder. This will ensure you get high-quality, consistent results and avoid the frustrating cycle of re-work. Here is a copy-pasteable list of rules and prompt templates you can save to a notepad and use throughout the entire refactor.

The Architect's Playbook: AI Coder Management
Core Rules: The Three Commandments
The Rule of the Fresh Slate:

Always start a brand new, clean chat session for each major Phase of the task_list.md (Phase 1, Phase 2, Phase 3).

Why: This is the most important rule. It prevents "context drift" and ensures the AI is always working with a clean, focused set of instructions, dramatically reducing the chance of strange errors or it forgetting key details.

The Rule of Complete Context:

The very first prompt in any new session must be the "Master Briefing Prompt." Never start with a small question. Always give the AI the full picture first.

The Rule of Single Tasking:

Give the AI one task at a time from your task_list.md. Do not ask it to build an entire EPIC at once.

Why: This breaks the work into small, manageable, and reviewable chunks. It makes it easy to catch errors early and ensures the AI stays focused on the immediate goal.

Prompt Library: Your Copy-Paste Toolkit
1. The Master Briefing Prompt (For Starting a New Phase)
Use this as the very first message in a new chat.

Hello. You are a Senior Backend Engineer and Software Architect with master-tier knowledge of Python, FastAPI, PostgreSQL, and modern, service-oriented game design.

Your task is to act as the lead developer for the V2 refactor of the GateGrind backend. Your work must be guided by the following three documents, which are your single, definitive source of truth.

### DOCUMENT 1: The Constitution (`project_rules.md`)


### DOCUMENT 2: The Master Blueprint (`refactor.md` / The GDD)


### DOCUMENT 3: The Construction Plan (`task_list.md`)


---

Acknowledge that you have read and fully understood all three documents. Confirm you understand that we are starting with **[INSERT CURRENT PHASE, e.g., PHASE 1: THE FOUNDATION]** and will proceed task by task. Await my first command.
2. The Task Execution Prompt (Your Main Workhorse)
Use this for every new task you start.

Excellent. We are now beginning **[INSERT EPIC NAME, e.g., EPIC 1: V2 Database Schema & Models]**.

Our first task is **[INSERT TASK ID & NAME, e.g., T1.2: SQLAlchemy Models Implementation]**.

Based on the specifications in the Master Blueprint (GDD) and the standards in the Constitution (`project_rules.md`), please generate the Python code for the following SQLAlchemy models: `Ascendant`, `Stat`.

Ensure the code is clean, well-commented, and includes all necessary imports and relationships.
3. The "Code Review" Prompt (For Quality Control)
Use this after the AI generates a piece of code to make it check its own work.

Thank you. Before we proceed, please perform a self-review of the code you just generated.

Check it against the following criteria from our `project_rules.md`:
1.  Does it adhere to our coding standards (naming conventions, typing)?
2.  Is the architecture sound (does it follow the service-oriented, API-first principles)?
3.  Are there any potential performance or security issues?

Provide a brief summary of your review. If you find any issues, provide the corrected code.
4. The "Testing" Prompt (To Ensure Robustness)
Use this after a service or endpoint is built.

The implementation of the `ProgressionService` looks good.

Now, as per our `project_rules.md`, we need comprehensive unit tests. Please generate the `pytest` code to test the `unlock_skill_node` method in `ProgressionService`.

The tests must cover:
1.  The "happy path" where a user successfully unlocks a node.
2.  The failure case where a user does not have enough Stat Points.
3.  The failure case where a user has not met the required Ascendant Level.
4.  Any other edge cases you can identify.
Your Workflow in Practice
It's a new day. You're starting Phase 2.

You open a brand new, clean chat with your AI.

You copy-paste the Master Briefing Prompt, filling in "PHASE 2: THE FEATURES".

The AI acknowledges.

You copy-paste a Task Execution Prompt for the first task in EPIC 5.

The AI generates the code.

You copy-paste the Code Review Prompt.

The AI reviews and confirms (or corrects) its work.

You copy-paste the Testing Prompt.

The AI generates the tests.

You mark the task as complete and move to the next Task Execution Prompt.

This disciplined, structured workflow is your ultimate "secret weapon." It transforms you from a simple user into a true AI Architect, guiding your powerful coder to build your vision with precision and quality, right the first time.