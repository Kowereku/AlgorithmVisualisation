


def convert_nx_to_cytoscape(nx_graph):
    """
    Converts the NetworkX 'Data Graph' (Blue Nodes) to Cytoscape.
    """
    elements = []
    for node, attributes in nx_graph.nodes(data=True):
        element = {
            "data": {"id": str(node), "label": str(node)},
            "classes": "data-node"
        }
        if "pos" in attributes:
            element["position"] = attributes["pos"]
        elements.append(element)

    for u, v, attributes in nx_graph.edges(data=True):
        weight = attributes.get('weight', '')
        elements.append({
            "data": {
                "source": str(u),
                "target": str(v),
                "weight": weight,
                "label": str(weight)
            },
            "classes": "data-edge"
        })
    return elements


def convert_vsdx_to_cytoscape(vsdx_data):
    """
    Converts the Parsed VSDX 'Schema' (Flowchart) to Cytoscape.
    Unknown or missing types are normalized to reasonable defaults so styling still works.
    """
    elements = []

    def normalize_type(raw_type, label_text):
        normalized = (raw_type or "").strip().lower()
        if normalized in {"process", "decision", "input", "output", "data", "terminator", "start", "end"}:
            return "terminator" if normalized in {"end"} else normalized or "process"
        if "start" in label_text.lower():
            return "start"
        if "end" in label_text.lower() or "stop" in label_text.lower():
            return "terminator"
        return "process"

    def normalize_name(raw_name, block_type, label_text):
        if raw_name:
            return raw_name
        # Provide a sensible default name for styling and tooltips when VSDX lacks a name
        if block_type == "start":
            return "Start"
        if block_type == "terminator":
            return "End"
        if block_type == "decision":
            return "Decision"
        return label_text or block_type.title()

    for block in vsdx_data.get("blocks", []):
        label = block.get("text", "")
        b_type = normalize_type(block.get("type", ""), label)
        b_name = normalize_name(block.get("name"), b_type, label)

        # Render end/terminator blocks with the same styling as start blocks for visual consistency
        class_suffix = "start" if b_type == "terminator" else b_type

        element = {
            "data": {
                "id": block["id"],
                "label": label,
                "type": b_type,
                "name": b_name
            },
            "classes": f"flow-{class_suffix}"
        }
        elements.append(element)

    for conn in vsdx_data.get("connections", []):
        elements.append({
            "data": {
                "source": conn["from_block_id"],
                "target": conn["to_block_id"],
                "label": conn.get("text", "")
            },
            "classes": "flow-edge"
        })

    return elements