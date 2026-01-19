def get_generate_prompt(parsed_data: dict) -> str:
    return f"""
You are a Senior Algorithm Visualization Architect.
Your task is to generate a **perfect, logic-complete** JSON schema for the requested algorithm.

**CONTEXT (Previous Examples):**
{parsed_data}

---

### **CRITICAL STRUCTURAL RULES (Algorithm Families):**

**1. DECISION TREES (Classification/Flow)**
* **Visual Metaphor:** A strict hierarchy. Root -> Branches -> Leaves.
* **Nodes:**
    * `Root` and `Questions`: Must be type **"decision"**.
    * `Outcomes/Leaves`: Must be type **"terminator"** (e.g., text: "Class: Apple", "Output: Yes").
* **Connections:** * Every edge coming FROM a "decision" block **MUST** have a `text` label (e.g., "Yes", "No", "< 5", ">= 5").
    * **NO DEAD ENDS:** Every path must eventually reach a "terminator".

**2. SORTING (Bubble, Quick, Merge, Heap)**
* **Visual Metaphor:** A linear loop comparing array indices.
* **Blocks:** Start -> Outer Loop -> Inner Loop -> Compare -> Swap -> End.
* **Logic:** The "Compare" decision needs explicit "Yes" (Swap) and "No" (Next) paths.

**3. RECURSIVE ALGORITHMS**
* **Structure:** Base case check -> Recursive call.
* **Required Blocks:** Start -> Base Case? (Decision) -> Recursive Step (Process) -> Return (Terminator).

---

### **STRICT JSON OUTPUT FORMAT:**
Your response must be a **SINGLE VALID JSON OBJECT**.

{{
  "title": "Exact Algorithm Name",
  "summary": "Concise summary.",
  "blocks": [
    {{ "id": "b1", "text": "Start", "type": "start" }},
    {{ "id": "b2", "text": "Is It Raining?", "type": "decision" }},
    {{ "id": "b3", "text": "Take Umbrella", "type": "terminator" }}
  ],
  "connections": [
    {{ "connector_id": "c1", "from_block_id": "b1", "to_block_id": "b2", "text": "" }},
    {{ "connector_id": "c2", "from_block_id": "b2", "to_block_id": "b3", "text": "Yes" }}
  ]
}}

**BLOCK TYPES:** "start", "terminator" (ends/leaves), "decision" (branching), "process" (actions), "io".

GENERATE THE JSON NOW.
"""