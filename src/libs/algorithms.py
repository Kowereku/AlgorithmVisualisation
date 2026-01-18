import networkx as nx
import heapq
import math


def get_scenario_data():
    G = nx.Graph()
    edges = [
        ("A", "B", 3), ("A", "J", 4), ("A", "G", 1),
        ("B", "D", 10), ("D", "H", 11), ("D", "J", 3),
        ("J", "G", 6), ("G", "F", 8), ("G", "E", 14),
        ("F", "H", 4), ("F", "I", 2), ("F", "E", 2),
        ("H", "C", 3), ("H", "I", 6), ("I", "E", 1)
    ]
    G.add_weighted_edges_from(edges)

    positions = {
        "A": {"x": 0, "y": 150}, "B": {"x": 100, "y": 50},
        "J": {"x": 150, "y": 150}, "G": {"x": 120, "y": 250},
        "D": {"x": 250, "y": 50}, "F": {"x": 300, "y": 200},
        "E": {"x": 250, "y": 350}, "H": {"x": 400, "y": 100},
        "I": {"x": 450, "y": 300}, "C": {"x": 550, "y": 120}
    }
    nx.set_node_attributes(G, positions, "pos")
    return G


def get_vsdx_id(vsdx_blocks, keywords):
    if not vsdx_blocks: return None
    for block in vsdx_blocks:
        txt = block.get("text", "").lower().strip()
        if not txt: continue
        for k in keywords:
            if k.lower() in txt:
                return block["id"]
    return None


def heuristic(node1, node2, graph):
    pos = nx.get_node_attributes(graph, "pos")
    x1, y1 = pos[node1]["x"], pos[node1]["y"]
    x2, y2 = pos[node2]["x"], pos[node2]["y"]
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)



def run_prim_simulation(graph, start_node="A", end_node=None, vsdx_blocks=None):
    keyword_map = {
        "init": ["Start Algorithm"],
        "check_q": ["Is Queue Empty"],
        "select": ["Select Minimum"],
        "check_v": ["Is Node Visited"],
        "add": ["Edge to Tree"],
        "expand": ["Neighbors"],
        "done": ["End Algorithm"]
    }
    ids = {k: get_vsdx_id(vsdx_blocks, v) for k, v in keyword_map.items()}

    trace = []
    mst_edges = []
    visited = {start_node}
    edges_pq = []

    for neighbor in graph.neighbors(start_node):
        w = graph[start_node][neighbor].get('weight', 1)
        heapq.heappush(edges_pq, (w, start_node, neighbor))

    step = 0
    trace.append({"step_id": step, "description": f"Start Prim's at {start_node}", "current_node": start_node,
                  "visited": list(visited), "path_found": [], "vsdx_id": ids["init"]})

    while edges_pq:
        step += 1
        trace.append(
            {"step_id": step, "description": "Checking Queue...", "current_node": None, "visited": list(visited),
             "path_found": [x[1] for x in mst_edges], "vsdx_id": ids["check_q"]})

        weight, u, v = heapq.heappop(edges_pq)

        trace.append({"step_id": step, "description": f"Selected {u}-{v} (Cost {weight})", "current_node": v,
                      "visited": list(visited), "path_found": [x[1] for x in mst_edges], "vsdx_id": ids["select"]})

        trace.append({"step_id": step, "description": f"Checking if {v} is visited...", "current_node": v,
                      "visited": list(visited), "path_found": [x[1] for x in mst_edges], "vsdx_id": ids["check_v"]})

        if v in visited: continue

        visited.add(v)
        mst_edges.append((u, v))

        trace.append({"step_id": step, "description": f"Added {v} to MST", "current_node": v, "visited": list(visited),
                      "path_found": [x[1] for x in mst_edges], "vsdx_id": ids["add"]})

        for neighbor in graph.neighbors(v):
            if neighbor not in visited:
                w = graph[v][neighbor].get('weight', 1)
                heapq.heappush(edges_pq, (w, v, neighbor))

        trace.append(
            {"step_id": step, "description": "Adding neighbors...", "current_node": v, "visited": list(visited),
             "path_found": [x[1] for x in mst_edges], "vsdx_id": ids["expand"]})

    trace.append({"step_id": step + 1, "description": "MST Done.", "current_node": start_node, "visited": list(visited),
                  "path_found": [x[1] for x in mst_edges], "vsdx_id": ids["done"]})
    return trace


def run_dijkstra_simulation(graph, start_node="A", end_node="C", vsdx_blocks=None):
    keyword_map = {
        "init": ["Start Algorithm"],
        "check_q":  ["Is Queue Empty"],
        "select": ["Select Best Node", "Lowest Cost"],
        "check_g": ["Is Goal Reached"],
        "update": ["Visit Neighbor"],
        "done": ["End Algorithm"]
    }
    ids = {k: get_vsdx_id(vsdx_blocks, v) for k, v in keyword_map.items()}

    trace = []
    open_set = []
    heapq.heappush(open_set, (0, start_node))
    came_from = {}
    g_score = {node: float('inf') for node in graph.nodes}
    g_score[start_node] = 0
    visited_history = []

    step = 0
    trace.append(
        {"step_id": step, "description": f"Start Dijkstra at {start_node}", "current_node": start_node, "visited": [],
         "path_found": [], "vsdx_id": ids["init"]})

    while open_set:
        step += 1
        trace.append({"step_id": step, "description": "Checking Queue...", "current_node": None,
                      "visited": list(visited_history), "path_found": [], "vsdx_id": ids["check_q"]})

        curr_cost, current = heapq.heappop(open_set)
        if current not in visited_history: visited_history.append(current)

        trace.append({"step_id": step, "description": f"Selected {current} (Cost {curr_cost})", "current_node": current,
                      "visited": list(visited_history), "path_found": [], "vsdx_id": ids["select"]})

        trace.append({"step_id": step, "description": "Checking Goal...", "current_node": current,
                      "visited": list(visited_history), "path_found": [], "vsdx_id": ids["check_g"]})

        if current == end_node:
            path = []
            temp = current
            while temp in came_from:
                path.append(temp)
                temp = came_from[temp]
            path.append(start_node)
            path.reverse()
            trace.append({"step_id": step + 1, "description": "Path Found!", "current_node": current,
                          "visited": list(visited_history), "path_found": path, "vsdx_id": ids["done"]})
            return trace

        for neighbor in graph.neighbors(current):
            weight = graph[current][neighbor].get('weight', 1)
            tentative_g = g_score[current] + weight

            if tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                heapq.heappush(open_set, (tentative_g, neighbor))

        trace.append({"step_id": step, "description": "Relaxing Edges...", "current_node": current,
                      "visited": list(visited_history), "path_found": [], "vsdx_id": ids["update"]})

    return trace


def run_astar_simulation(graph, start_node="A", end_node="C", vsdx_blocks=None):
    keyword_map = {
        "init": ["Start Algorithm"],
        "check_q": ["Is Queue Empty"],
        "select": ["Lowest F-score"],
        "check_g": ["Is Goal Reached"],
        "calc": ["Visit Neighbor"],
        "done": ["End Algorithm"]
    }
    ids = {k: get_vsdx_id(vsdx_blocks, v) for k, v in keyword_map.items()}

    trace = []
    open_set = []
    h_start = heuristic(start_node, end_node, graph)
    heapq.heappush(open_set, (h_start, start_node))
    came_from = {}
    g_score = {node: float('inf') for node in graph.nodes}
    g_score[start_node] = 0
    f_score = {node: float('inf') for node in graph.nodes}
    f_score[start_node] = h_start
    visited_history = []

    step = 0
    trace.append(
        {"step_id": step, "description": f"Start A* at {start_node}", "current_node": start_node, "visited": [],
         "path_found": [], "vsdx_id": ids["init"]})

    while open_set:
        step += 1
        trace.append({"step_id": step, "description": "Checking Queue...", "current_node": None,
                      "visited": list(visited_history), "path_found": [], "vsdx_id": ids["check_q"]})

        curr_f, current = heapq.heappop(open_set)
        if current not in visited_history: visited_history.append(current)

        trace.append(
            {"step_id": step, "description": f"Selected {current} (F-Score: {curr_f:.1f})", "current_node": current,
             "visited": list(visited_history), "path_found": [], "vsdx_id": ids["select"]})

        trace.append({"step_id": step, "description": "Checking Goal...", "current_node": current,
                      "visited": list(visited_history), "path_found": [], "vsdx_id": ids["check_g"]})

        if current == end_node:
            path = []
            temp = current
            while temp in came_from:
                path.append(temp)
                temp = came_from[temp]
            path.append(start_node)
            path.reverse()
            trace.append({"step_id": step + 1, "description": "Goal Found!", "current_node": current,
                          "visited": list(visited_history), "path_found": path, "vsdx_id": ids["done"]})
            return trace

        for neighbor in graph.neighbors(current):
            weight = graph[current][neighbor].get('weight', 1)
            tentative_g = g_score[current] + weight

            if tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                h = heuristic(neighbor, end_node, graph)
                f_score[neighbor] = tentative_g + h
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

        trace.append({"step_id": step, "description": "Updating Costs & Heuristics...", "current_node": current,
                      "visited": list(visited_history), "path_found": [], "vsdx_id": ids["calc"]})

    return trace