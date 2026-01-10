


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
    """
    elements = []

    for block in vsdx_data.get("blocks", []):
        b_type = block.get("type", "process")

        element = {
            "data": {
                "id": block["id"],
                "label": block["text"],
                "type": b_type
            },
            "classes": f"flow-{b_type}"
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