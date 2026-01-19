def get_data_setup_prompt(user_request: str) -> str:
    return f"""
You are a Python Code Generator for an Algorithm Visualization App.
The user wants to visualize: "{user_request}".

**Task:**
Write a Python function named `get_data()` that returns the initial data structure.

**CRITICAL RULES:**
1. **RETURN TYPE:** You MUST return a `networkx.Graph` object. 
   - **NEVER return a dict or list.** - For Sorting (Bubble, Quick, etc.), represent indices as Nodes (0, 1, 2...).
   - Example: `G = nx.Graph()` ... `G.add_node("0", value=5)`
2. **Fixed Seed:** Start with `random.seed(42)` for stability.
3. **LAYOUT (Crucial):** You MUST assign `pos` to every node.
   - **For Sorting:** `pos = {{str(i): {{"x": i * 80, "y": 0}} for i in range(n)}}` (Linear).
   - **For Trees/Graphs:** `pos = nx.spring_layout(G, seed=42)`.
4. **Data Size:** Small (max 6 items).

**Output format:**
Return ONLY valid Python code. No markdown.
"""

def get_simulation_logic_prompt(user_request: str, block_list: str, data_code_context: str) -> str:
    return f"""
You are a Python Code Generator.
Task: Write `run_simulation(graph, vsdx_blocks)`.

**User Request:** {user_request}

**Context (Data):**
{data_code_context}

**Context (Flowchart Blocks):**
{block_list}

**CRITICAL RULES:**
1. **Function Signature:** `def run_simulation(graph, vsdx_blocks):`
2. **Block Access:** `vsdx_blocks` is a **LIST** of dictionaries.
   - **ERROR TRAP:** Do NOT use `vsdx_blocks.items()`. It will crash.
   - **CORRECT:** Iterate with `for block in vsdx_blocks:` or use `get_id(vsdx_blocks, "Keyword")`.
3. **Trace Format:**
   {{
       "step_id": int,
       "description": "text",
       "current_node": "0",       
       "visited": ["0", "1"],     
       "path_found": ["0", "1"], 
       "vsdx_id": "BLOCK_ID",
       "data_values": {{ "0": 5, "1": 2 }},
       "node_colors": {{ "0": "#FFD700" }}
   }}

**Output format:**
Return ONLY valid Python code. No markdown.
"""

def get_fix_code_prompt(broken_pkg: dict, error_msg: str) -> str:
    return f"""
You are a Python Code Repair Expert.
The previously generated code failed validation.

**Error Message:**
{error_msg}

**Broken Data Setup Code:**
{broken_pkg.get('data_code')}

**Broken Simulation Code:**
{broken_pkg.get('sim_code')}

**Task:**
Fix the code.
- **Dict Error:** If error is "returned dict", rewrite `get_data` to return `nx.Graph`.
- **List Attribute Error:** If error is "'list' object has no attribute 'items'", you are calling `.items()` on `vsdx_blocks`. 
  - **FIX:** Remove `.items()`. Iterate over the list directly: `for block in vsdx_blocks:`.

**Required JSON Structure:**
{{
    "data_code": "Corrected python code...",
    "sim_code": "Corrected python code..."
}}

**Output format:**
Return ONLY valid JSON. No markdown.
"""