def get_generate_prompt(parsed_data: dict) -> str:
    """
    Generate a strict prompt for creating a new schema.
    """
    return f"""
You are an advanced AI assistant. Your ONLY task is to generate a new schema that follows the exact JSON structure defined below.

IMPORTANT: 
1. The response must contain ONLY a single valid JSON object.
2. Do NOT write markdown formatting (like ```json).
3. Do NOT include explanations.

**Required JSON Structure:**
The output object must have exactly these 4 top-level keys:
{{
  "title": "A short, descriptive title for this algorithm (max 5 words)",
  "summary": "A one-sentence summary of what this algorithm does",
  "blocks": [ ... array of block objects ... ],
  "connections": [ ... array of connection objects ... ]
}}

**Block Object Definition:**
- "id": string (unique)
- "text": string (content displayed in block)
- "type": string (choose from: "start", "stop", "process", "decision", "io")

**Connection Object Definition:**
- "connector_id": string (unique)
- "from_block_id": string (matches a block id)
- "to_block_id": string (matches a block id)
- "text": string (label for the line, e.g., "Yes", "No", or empty)

**Context / Example Pattern:**
Use the logic or style from this parsed data (but generate a NEW distinct scenario based on user input):
{parsed_data}

Generate the JSON now.
"""
