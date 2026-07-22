"""Curated test dataset of evaluation questions and ground truth answers."""

TEST_QUESTIONS = [
    # --- Category: Conflict Detection (Triggers CONFLICTING status) ---
    {
        "question": "What is the employee vacation policy and how many days are allowed annually?",
        "reference": "According to the Employee Handbook v1.0 (effective 2024-01-01), employees receive 15 days of paid annual vacation. However, the Benefits Addendum v1.1 (effective 2024-07-01) updates this to 20 days. This creates a document conflict regarding annual vacation allowance.",
        "category": "conflict_detection"
    },
    {
        "question": "What is the policy on remote work eligibility?",
        "reference": "The Policy Document v1.0 states that employees must work in the office 4 days a week (1 day remote). However, the Remote Work Addendum v2.0 (effective 2024-06-15) states that employees are only required to be in the office 2 days a week (3 days remote). This is a direct conflict.",
        "category": "conflict_detection"
    },
    {
        "question": "What is the threshold for travel expense pre-approval?",
        "reference": "The Expense Policy (effective 2024-01-01) sets the pre-approval threshold for travel expenses at $500. However, the Revised Finance Memo (effective 2024-05-01) lowers this threshold to $250. This constitutes a conflict in the approval thresholds.",
        "category": "conflict_detection"
    },
    # --- Category: Insufficient Context (Triggers INSUFFICIENT status) ---
    {
        "question": "What is the maternity leave duration for part-time contractors?",
        "reference": "The retrieved documents only detail maternity leave for full-time employees (12 weeks). There is no policy or mention regarding maternity leave or benefits for part-time contractors, making this query's context insufficient.",
        "category": "insufficient_context"
    },
    {
        "question": "Who is the external auditor mentioned in the Q4 financial report?",
        "reference": "The provided financial reports for Q1 do not mention the Q4 report or specify the name of the external auditor. The information is not present in the ingested dataset.",
        "category": "insufficient_context"
    },
    {
        "question": "What are the specific penalties for violating the intellectual property agreement?",
        "reference": "While the code of conduct mentions that intellectual property must be protected, the exact penalties or legal consequences of violating the IP agreement are not detailed in the available text.",
        "category": "insufficient_context"
    },
    # --- Category: OCR Noise / Complex Documents (Triggers SUFFICIENT but messy) ---
    {
        "question": "What is the Q1 revenue and net income for 2024?",
        "reference": "According to the Q1 Financial Report, the revenue was $12.5 million and the net income was $1.8 million.",
        "category": "ocr_noise"
    },
    {
        "question": "What is the serial number of the industrial printer and its warranty expiry?",
        "reference": "According to the equipment scan sheet, the printer model is 'PrintMaster 5000' with Serial Number 'SN-998822-X' and the warranty expires on 2026-12-31.",
        "category": "ocr_noise"
    },
    {
        "question": "What are the rules regarding overtime pay according to section 4.2?",
        "reference": "According to Section 4.2 of the Employee Handbook, overtime is paid at 1.5x the standard hourly rate for any hours worked beyond 40 hours per week, and requires manager pre-approval.",
        "category": "sufficient"
    },
    {
        "question": "What is the standard notice period for voluntary resignation?",
        "reference": "The standard notice period for voluntary resignation is 30 days for general staff and 60 days for executive/management-level employees, as specified in the HR Policy.",
        "category": "sufficient"
    }
]
