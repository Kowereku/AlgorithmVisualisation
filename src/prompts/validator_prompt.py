def get_validator_prompt(generated_schema: dict, user_request: str) -> str:
    schema_str = str(generated_schema)[:15000]

    return f"""
You are a **Strict Algorithm QA Validator**.
Your job is to REJECT any visualization schema that is broken, incomplete, or illogical.

**User Request:** "{user_request}"

**Generated Schema to Validate:**
{schema_str}

---

### **VALIDATION CHECKLIST:**

1.  **Topology & Termination:**
    * Does the graph START at a "start" block?
    * Does EVERY path eventually reach a "terminator" block? (CRITICAL for Decision Trees).
    * Are all "decision" blocks actually branching (do they have at least 2 outgoing edges)?

2.  **Logic Completeness:**
    * If this is a **Sort**, are there explicit "Compare" AND "Swap" steps?
    * If this is a **Tree**, are there explicit **Leaf Nodes** (terminators)?
    * Is the algorithm actually complex enough? (A chart with just "Start" -> "Process" -> "End" is FAIL).

3.  **Data Integrity:**
    * Are all `from_block_id` and `to_block_id` valid existing block IDs?

---

### **RESPONSE FORMAT (JSON ONLY):**

If the schema is **PERFECT**:
{{
    "status": "PASS",
    "critique": "Structure is valid and logic is complete."
}}

If the schema is **FLAWED**:
{{
    "status": "FAIL",
    "critique": "EXPLAIN EXACTLY WHAT IS WRONG (e.g., 'Decision block b3 has no Leaf/Terminator').",
    "fixed_schema": {{ ... THE FULLY CORRECTED JSON SCHEMA ... }}
}}

**NOTE:** If you return "FAIL", you **MUST** provide the `fixed_schema`. Do not just complain, FIX IT.

ANALYZE NOW.
"""