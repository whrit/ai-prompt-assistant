from typing import List, Dict

# key: stable identifier used for remembering A/B choices
TEMPLATES: List[Dict] = [
    {"key": "email_reply", "name": "Email reply (polished)", "prompt": "Draft a concise, polite reply:\n\nContext:\n{context}\n\nConstraints: 3-5 sentences, positive tone, end with a clear next step."},
    {"key": "bug_report", "name": "Bug report (steps+expected/actual)", "prompt": "Turn this into a crisp bug report:\n\nContext:\n{context}\n\nInclude: Environment, Steps to Reproduce, Expected, Actual, Attachments (if any)."},
    {"key": "meeting_notes", "name": "Meeting → decisions & actions", "prompt": "Summarize meeting notes into: Decisions, Action Items (owner+due), Risks/Blockers, Open Questions.\n\nNotes:\n{context}"},
    {"key": "job_tailor", "name": "Job application tailoring", "prompt": "Tailor the resume bullets to this JD:\n\nJob:\n{context}\n\nOutput: 4-6 targeted bullets with metrics and relevant keywords."},
    {"key": "sql_helper", "name": "SQL helper (schema Qs)", "prompt": "Given this question, ask any missing schema clarifications then propose a SQL query:\n\nQuestion:\n{context}\n\nOutput: Clarifications, Proposed SQL, Explanation."},
    {"key": "code_fix", "name": "Code fix + explanation", "prompt": "Find and fix the bug in:\n\n{context}\n\nOutput: Patched snippet and a short explanation. Unit-test idea if relevant."},
    {"key": "exec_summary", "name": "Executive summary (TL;DR)", "prompt": "Create an executive summary of:\n\n{context}\n\nOutput: TL;DR (3 bullets), Key Facts, Risks, Next Steps."},
    {"key": "brainstorm", "name": "Brainstorm 10 ideas", "prompt": "Generate 10 distinct ideas for:\n\n{context}\n\nVary tone, audience, and angle. Group in 3 themes."},
    {"key": "translate", "name": "Translate & preserve formatting", "prompt": "Translate while preserving Markdown/structure:\n\n{context}\n\nSpecify any ambiguous terms."},
    {"key": "tasks_extract", "name": "Extract actionable tasks", "prompt": "Extract actionable tasks from:\n\n{context}\n\nOutput: checklist with owner (if any), due date guess, dependencies."},
]