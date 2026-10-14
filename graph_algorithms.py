"""Python implementations of the graph algorithms used by Graph Theory Lab."""

from __future__ import annotations

from collections import deque
from html import escape
import heapq
import math
from itertools import combinations
from typing import Any


_PALETTE = [
    "#ef7d57", "#41a6f6", "#a7f070", "#ffcd75", "#f4a6d7",
    "#73eff7", "#b13e53", "#38b764", "#c28a4a", "#94b0c2",
    "#5d275d", "#3b5dc9", "#257179", "#d4a5ff", "#566c86",
]


def _fmt(value: float | int) -> str:
    if math.isinf(value):
        return "∞"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return f"{value:g}"


def _name(names: dict[int, str], node_id: int) -> str:
    return names.get(node_id, f"v{node_id}")


def _html(value: Any) -> str:
    return escape(str(value), quote=True)


def _step(message: str, **state: dict[str, Any]) -> dict[str, Any]:
    return {
        "msg": message,
        "ntext": state.get("ntext"),
        "node": state.get("node", {}),
        "edge": state.get("edge", {}),
        "etext": state.get("etext"),
        "fill": state.get("fill"),
    }


def _card(label: str, value: Any) -> str:
    return f'<div class="card"><div class="k">{label}</div><div class="v">{value}</div></div>'


def _result(title: str, key: str, steps: list[dict[str, Any]], summary: str, **extra: Any) -> dict[str, Any]:
    return {"title": title, "key": key, "steps": steps, "summary": summary, **extra}


def _graph(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[int, str], bool]:
    nodes = payload.get("nodes")
    edges = payload.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("ข้อมูลกราฟไม่ถูกต้อง")
    node_ids: list[int] = []
    names: dict[int, str] = {}
    for node in nodes:
        if not isinstance(node, dict) or not isinstance(node.get("id"), int):
            raise ValueError("ข้อมูลจุดยอดไม่ถูกต้อง")
        node_id = node["id"]
        if node_id in names:
            raise ValueError("พบรหัสจุดยอดซ้ำ")
        node_ids.append(node_id)
        names[node_id] = str(node.get("label", f"v{node_id}"))
    valid_ids = set(node_ids)
    cleaned_edges: list[dict[str, Any]] = []
    for edge in edges:
        if not isinstance(edge, dict) or not isinstance(edge.get("id"), int):
            raise ValueError("ข้อมูลเส้นเชื่อมไม่ถูกต้อง")
        u, v, weight = edge.get("u"), edge.get("v"), edge.get("w")
        if not isinstance(u, int) or not isinstance(v, int) or u not in valid_ids or v not in valid_ids:
            raise ValueError("เส้นเชื่อมอ้างถึงจุดยอดที่ไม่มีอยู่")
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not math.isfinite(weight):
            raise ValueError("น้ำหนักหรือความจุของเส้นเชื่อมไม่ถูกต้อง")
        cleaned_edges.append({"id": edge["id"], "u": u, "v": v, "w": weight})
    return nodes, cleaned_edges, names, bool(payload.get("directed"))


def _dijkstra(payload: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, names, directed = _graph(payload)
    ids = [node["id"] for node in nodes]
    source, sink = payload.get("source"), payload.get("sink")
    if not ids:
        raise ValueError("ยังไม่มีจุดยอด")
    if source not in names:
        raise ValueError('กรุณาเลือก "ต้นทาง" ก่อนรัน Dijkstra')
    negative = [edge for edge in edges if edge["w"] < 0]
    if negative:
        edges_list = ", ".join(f'{_name(names, edge["u"])}–{_name(names, edge["v"])}' for edge in negative)
        raise ValueError(f"Dijkstra ใช้ไม่ได้กับน้ำหนักติดลบ: {edges_list}")

    adj: dict[int, list[tuple[int, float, int]]] = {node_id: [] for node_id in ids}
    for edge in edges:
        adj[edge["u"]].append((edge["v"], edge["w"], edge["id"]))
        if not directed:
            adj[edge["v"]].append((edge["u"], edge["w"], edge["id"]))
    distances = {node_id: math.inf for node_id in ids}
    previous: dict[int, int | None] = {node_id: None for node_id in ids}
    previous_edge: dict[int, int] = {}
    done: set[int] = set()
    steps: list[dict[str, Any]] = []
    relax_count = 0
    distances[source] = 0

    def state() -> dict[str, Any]:
        return {
            "ntext": {node_id: _fmt(distances[node_id]) for node_id in ids},
            "node": {node_id: "visited" for node_id in done},
            "edge": {edge_id: "soft" for edge_id in previous_edge.values()},
        }

    def snap(message: str, node: dict[int, str] | None = None, edge: dict[int, str] | None = None) -> None:
        current = state()
        if node:
            current["node"].update(node)
        if edge:
            current["edge"].update(edge)
        steps.append(_step(message, **current))

    snap(f"เริ่มต้น: d({_name(names, source)}) = 0 และจุดอื่นทั้งหมด = ∞", {source: "current"})
    while True:
        available = [node_id for node_id in ids if node_id not in done and distances[node_id] < math.inf]
        if not available:
            remaining = [node_id for node_id in ids if node_id not in done]
            if remaining:
                labels = ", ".join(names[node_id] for node_id in remaining)
                snap(f"จุดที่เหลือ ({labels}) เข้าไม่ถึงจากต้นทาง → ระยะ = ∞")
            break
        current = min(available, key=lambda node_id: distances[node_id])
        best_distance = distances[current]
        done.add(current)
        snap(f"เลือก {_name(names, current)} ซึ่งมีระยะน้อยที่สุด ({_fmt(best_distance)}) ในจุดที่ยังไม่ปิด → ปิดจุดนี้ (ระยะนี้คือคำตอบสุดท้ายแล้ว)", {current: "current"})
        for target, weight, edge_id in adj[current]:
            if target in done:
                continue
            relax_count += 1
            candidate = distances[current] + weight
            old = distances[target]
            if candidate < old:
                distances[target] = candidate
                previous[target] = current
                previous_edge[target] = edge_id
                message = f"Relax {_name(names, current)} → {_name(names, target)}: {_fmt(distances[current])} + {_fmt(weight)} = {_fmt(candidate)} < {_fmt(old)} ✔ อัปเดต d({_name(names, target)}) = {_fmt(candidate)}"
                snap(message, {current: "current", target: "consider"}, {edge_id: "consider"})
            else:
                message = f"Relax {_name(names, current)} → {_name(names, target)}: {_fmt(distances[current])} + {_fmt(weight)} = {_fmt(candidate)} ≥ {_fmt(old)} ✘ ไม่เปลี่ยน"
                snap(message, {current: "current", target: "consider"}, {edge_id: "reject"})

    def path_to(target: int) -> list[int] | None:
        if math.isinf(distances[target]):
            return None
        path: list[int] = []
        current: int | None = target
        while current is not None:
            path.append(current)
            current = previous[current]
        return list(reversed(path))

    has_sink = sink in names
    path = path_to(sink) if has_sink else None
    path_edges: list[int] = []
    if path:
        current = sink
        while previous[current] is not None:
            path_edges.append(previous_edge[current])
            current = previous[current]
        snap(
            f"✔ เสร็จสิ้น! เส้นทางสั้นที่สุด: {' → '.join(_name(names, node_id) for node_id in path)} | ระยะรวม = {_fmt(distances[sink])}",
            {node_id: "path" for node_id in path},
            {edge_id: "path" for edge_id in path_edges},
        )
    elif has_sink:
        snap(f"✘ เสร็จสิ้น: ไม่มีเส้นทางจาก {_name(names, source)} ไป {_name(names, sink)} (ระยะ = ∞)")
    else:
        snap("✔ เสร็จสิ้น! ตัวเลขเหนือจุด = ระยะทางสั้นที่สุดจากต้นทาง (เลือก \"ปลายทาง\" เพื่อดูเส้นทาง)")

    summary = ""
    if has_sink:
        if path:
            route = " → ".join(f'<span class="chip">{_html(_name(names, node_id))}</span>' for node_id in path)
            summary += f'<div class="hero">🚚 ระยะทางสั้นที่สุดจาก <b>{_html(_name(names, source))}</b> ไป <b>{_html(_name(names, sink))}</b> = <span class="bignum">{_fmt(distances[sink])}</span><div class="route">{route}</div></div>'
        else:
            summary += f'<div class="hero bad">✘ ไปไม่ถึง {_html(_name(names, sink))} จาก {_html(_name(names, source))} (ระยะ = ∞)</div>'
    reachable = sum(not math.isinf(distances[node_id]) for node_id in ids)
    summary += '<div class="cards">' + _card("ต้นทาง", _html(_name(names, source))) + _card("ไปถึงได้", f"{reachable} / {len(nodes)} จุด") + _card("จำนวนครั้ง Relax", relax_count) + _card("จำนวนขั้นตอน", len(steps)) + "</div>"
    summary += '<h3>ระยะทางจากต้นทางไปทุกจุด</h3><div class="tw"><table class="tbl"><tr><th>จุดยอด</th><th>ระยะ</th><th>เส้นทาง</th></tr>'
    for node in sorted(nodes, key=lambda n: (distances[n["id"]], n["id"])):
        target = node["id"]
        path = path_to(target)
        route = " → ".join(_html(_name(names, path_id)) for path_id in path) if path else "เข้าไม่ถึง"
        summary += f'<tr><td class="l">{_html(names[target])}</td><td><b>{_fmt(distances[target])}</b></td><td class="l">{route}</td></tr>'
    summary += "</table></div><div class=\"note\">ใช้หาเส้นทางขนส่งที่สั้นที่สุดหรือถูกที่สุดจากคลังสินค้าไปยังร้านค้า/ลูกค้า ถ้าน้ำหนักคือ \"ค่าขนส่ง\" ผลลัพธ์จะเป็นเส้นทางที่ประหยัดที่สุด</div>"
    return _result("📊 สรุปผล Dijkstra — เส้นทางสั้นที่สุด", "dijkstra", steps, summary)


def _traversal(payload: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, names, directed = _graph(payload)
    ids = [node["id"] for node in nodes]
    source = payload.get("source")
    if not ids:
        raise ValueError("??????????????")
    if source not in names:
        raise ValueError('?????????? "??????" ?????????????????')
    if len(ids) > 5000 or len(edges) > 10000:
        raise ValueError("BFS ???????? 5,000 ????????? 10,000 ????")

    adjacency: dict[int, list[tuple[int, int]]] = {node_id: [] for node_id in ids}
    for edge in edges:
        adjacency[edge["u"]].append((edge["v"], edge["id"]))
        if not directed:
            adjacency[edge["v"]].append((edge["u"], edge["id"]))
    queue = deque([source])
    discovered = {source}
    visited: set[int] = set()
    tree_edges: set[int] = set()
    order: list[int] = []
    steps: list[dict[str, Any]] = [_step(f"BFS ???????? {_name(names, source)}", node={source: "current"})]

    while queue:
        current = queue.popleft()
        visited.add(current)
        order.append(current)
        for target, edge_id in adjacency[current]:
            if target in discovered:
                continue
            discovered.add(target)
            queue.append(target)
            tree_edges.add(edge_id)
        steps.append(_step(
            f"?????? {_name(names, current)}; Queue = "
            f"[{', '.join(_name(names, node_id) for node_id in queue)}]",
            node={**{node_id: "visited" for node_id in visited}, current: "current"},
            edge={edge_id: "soft" for edge_id in tree_edges},
        ))

    unreachable = [node_id for node_id in ids if node_id not in visited]
    summary = (
        f'<div class="hero">BFS ???????? {_html(_name(names, source))}</div>'
        f'<p><b>??????????????:</b> {" ? ".join(_html(_name(names, node_id)) for node_id in order)}</p>'
        f'<p><b>Tree edges:</b> {len(tree_edges)} ? ?????????? {len(order)} / {len(ids)} ???</p>'
    )
    if unreachable:
        summary += f'<div class="hero warn">??????????: {", ".join(_html(_name(names, node_id)) for node_id in unreachable)}</div>'
    return _result("BFS", "bfs", steps, summary, order=order, treeEdges=sorted(tree_edges))


def _prim(payload: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, names, directed = _graph(payload)
    if directed:
        raise ValueError("Prim ใช้ได้เฉพาะกราฟไม่มีทิศทาง")
    ids = [node["id"] for node in nodes]
    if not ids:
        raise ValueError("ยังไม่มีจุดยอด")
    source = payload.get("source")
    start = source if source in names else ids[0]
    in_tree: set[int] = set()
    selected: list[tuple[dict[str, Any], int, float]] = []
    roots: list[int] = []
    total: float = 0
    steps: list[dict[str, Any]] = []

    def base() -> dict[str, dict[int, str]]:
        return {
            "node": {node_id: "visited" for node_id in in_tree},
            "edge": {edge["id"]: "tree" for edge, _, _ in selected},
        }

    def snap(message: str, node: dict[int, str] | None = None, edge: dict[int, str] | None = None) -> None:
        current = base()
        if node:
            current["node"].update(node)
        if edge:
            current["edge"].update(edge)
        steps.append(_step(message, **current))

    order = [start, *(node_id for node_id in ids if node_id != start)]
    for root in order:
        if root in in_tree:
            continue
        tree_number = len(roots) + 1
        roots.append(root)
        in_tree.add(root)
        message = f"เริ่มต้นที่ {_name(names, root)} — ต้นไม้มี 1 จุด น้ำหนักรวม = 0" if tree_number == 1 else f"ไม่มีเส้นไปยังจุดที่เหลือแล้ว (กราฟไม่ Connected) → เริ่มต้นไม้ต้นที่ {tree_number} ที่ {_name(names, root)}"
        snap(message, {root: "current"})
        while True:
            candidates = [edge for edge in edges if edge["u"] != edge["v"] and ((edge["u"] in in_tree) != (edge["v"] in in_tree))]
            if not candidates:
                break
            best = min(candidates, key=lambda edge: edge["w"])
            edge_state = {edge["id"]: "consider" for edge in candidates}
            candidate_list = ", ".join(f'{_name(names, e["u"])}–{_name(names, e["v"])} ({_fmt(e["w"])})' for e in sorted(candidates, key=lambda e: e["w"])[:6])
            if len(candidates) > 6:
                candidate_list += ", ..."
            snap(f"ตัวเลือก {len(candidates)} เส้นที่เชื่อมต้นไม้กับจุดใหม่: {candidate_list}", edge=edge_state)
            new_node = best["v"] if best["u"] in in_tree else best["u"]
            in_tree.add(new_node)
            total += best["w"]
            selected.append((best, tree_number, total))
            snap(f"✔ เลือกเส้นต้นทุนต่ำสุด {_name(names, best['u'])}–{_name(names, best['v'])} = {_fmt(best['w'])} → เพิ่ม {_name(names, new_node)} | น้ำหนักรวม = {_fmt(total)}", {new_node: "current"}, {best["id"]: "path"})

    tree_count = len(roots)
    snap(f"✔ เสร็จสิ้น! Minimum Spanning Tree มี {len(selected)} เส้น น้ำหนักรวม = {_fmt(total)}" if tree_count == 1 else f"✔ เสร็จสิ้น! ได้ Spanning Forest {tree_count} ต้น ({len(selected)} เส้น) น้ำหนักรวม = {_fmt(total)}")
    label = "Minimum Spanning Tree" if tree_count == 1 else f"Spanning Forest ({tree_count} ต้น)"
    summary = f'<div class="hero {"warn" if tree_count > 1 else ""}">🌳 {label} น้ำหนักรวมต่ำสุด = <span class="bignum">{_fmt(total)}</span></div>'
    summary += '<div class="cards">' + _card("จุดเริ่ม", _html(_name(names, start))) + _card("จำนวนเส้นที่ใช้", f"{len(selected)} = |V| − {tree_count}") + _card("จำนวนต้นไม้", tree_count) + _card("เส้นที่ไม่ใช้", len(edges) - len(selected)) + "</div>"
    if tree_count > 1:
        roots_html = " ".join(f'<span class="chip">{_html(_name(names, root))}</span>' for root in roots)
        summary += f"<p>⚠ กราฟไม่ Connected จึงได้ป่า (Forest) — เริ่มแต่ละต้นที่: {roots_html}</p>"
    summary += '<h3>ลำดับเส้นที่เลือก</h3><div class="tw"><table class="tbl"><tr><th>#</th><th>ต้นที่</th><th>เส้น</th><th>น้ำหนัก</th><th>รวมสะสม</th></tr>'
    for index, (edge, tree_number, cumulative) in enumerate(selected, 1):
        summary += f'<tr><td>{index}</td><td>{tree_number}</td><td class="l">{_html(_name(names, edge["u"]))} – {_html(_name(names, edge["v"]))}</td><td>{_fmt(edge["w"])}</td><td><b>{_fmt(cumulative)}</b></td></tr>'
    summary += "</table></div><div class=\"note\">วางโครงข่ายถนน ท่อประปา หรือสายไฟให้ทุกจุดเชื่อมถึงกัน โดยใช้งบประมาณรวมน้อยที่สุด</div>"
    return _result("📊 สรุปผล Prim — Minimum Spanning Tree", "prim", steps, summary)


def _kruskal(payload: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, names, directed = _graph(payload)
    ids = [node["id"] for node in nodes]
    if directed:
        raise ValueError("Kruskal ใช้ได้เฉพาะกราฟไม่มีทิศทาง")
    if not ids:
        raise ValueError("ยังไม่มีจุดยอด")

    parent = {node_id: node_id for node_id in ids}
    rank = {node_id: 0 for node_id in ids}

    def find(node_id: int) -> int:
        while parent[node_id] != node_id:
            parent[node_id] = parent[parent[node_id]]
            node_id = parent[node_id]
        return node_id

    def union(left: int, right: int) -> bool:
        root_left, root_right = find(left), find(right)
        if root_left == root_right:
            return False
        if rank[root_left] < rank[root_right]:
            root_left, root_right = root_right, root_left
        parent[root_right] = root_left
        if rank[root_left] == rank[root_right]:
            rank[root_left] += 1
        return True

    steps: list[dict[str, Any]] = [_step("เรียงเส้นจากน้ำหนักน้อยไปมาก")]
    chosen: list[dict[str, Any]] = []
    total = 0
    for edge in sorted(edges, key=lambda item: (item["w"], item["id"])):
        if union(edge["u"], edge["v"]):
            chosen.append(edge)
            total += edge["w"]
            steps.append(_step(
                f"เลือก {_name(names, edge['u'])}–{_name(names, edge['v'])} ({_fmt(edge['w'])}); รวม = {_fmt(total)}",
                node={edge["u"]: "visited", edge["v"]: "visited"},
                edge={edge["id"]: "tree"},
            ))
        else:
            steps.append(_step(
                f"ข้าม {_name(names, edge['u'])}–{_name(names, edge['v'])} ({_fmt(edge['w'])}) เพราะจะเกิดวงจร",
                edge={edge["id"]: "reject"},
            ))

    component_roots = {find(node_id) for node_id in ids}
    components = len(component_roots)
    forest_edges = {edge["id"] for edge in chosen}
    steps.append(_step(
        f"เสร็จสิ้น: {'Minimum Spanning Tree' if components == 1 else 'Spanning Forest'} รวม {_fmt(total)}",
        edge={edge_id: "tree" for edge_id in forest_edges},
        node={node_id: "visited" for node_id in ids},
    ))
    summary = (
        f'<div class="hero">{"Minimum Spanning Tree" if components == 1 else "Spanning Forest"}'
        f' • น้ำหนักรวม = <b>{_fmt(total)}</b> • {components} component(s)</div>'
        '<h3>เส้นที่เลือก</h3><div class="tw"><table class="tbl"><tr><th>#</th><th>เส้น</th><th>น้ำหนัก</th></tr>'
    )
    for index, edge in enumerate(chosen, 1):
        summary += (
            f'<tr><td>{index}</td><td class="l">{_html(_name(names, edge["u"]))}–'
            f'{_html(_name(names, edge["v"]))}</td><td>{_fmt(edge["w"])}</td></tr>'
        )
    summary += "</table></div>"
    return _result("Kruskal — Minimum Spanning Forest", "kruskal", steps, summary, total=total)


def _connectivity(payload: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, names, directed = _graph(payload)
    ids = [node["id"] for node in nodes]
    if directed:
        raise ValueError("Bridge และ Articulation Point ใช้กับกราฟไม่มีทิศทาง")
    if len(ids) > 900:
        raise ValueError("Connectivity จำกัดที่ 900 จุดยอด เพื่อป้องกัน stack overflow")

    adjacency: dict[int, list[tuple[int, int]]] = {node_id: [] for node_id in ids}
    for edge in edges:
        adjacency[edge["u"]].append((edge["v"], edge["id"]))
        adjacency[edge["v"]].append((edge["u"], edge["id"]))

    discovery: dict[int, int] = {}
    low: dict[int, int] = {}
    articulation: set[int] = set()
    bridges: set[int] = set()
    steps: list[dict[str, Any]] = [_step("DFS low-link: เปรียบเทียบ discovery time กับ low-link")]
    timestamp = 0
    components = 0

    def visit(node_id: int, parent_edge: int | None) -> None:
        nonlocal timestamp
        timestamp += 1
        discovery[node_id] = low[node_id] = timestamp
        child_count = 0
        for neighbor, edge_id in adjacency[node_id]:
            if edge_id == parent_edge:
                continue
            if neighbor not in discovery:
                child_count += 1
                visit(neighbor, edge_id)
                low[node_id] = min(low[node_id], low[neighbor])
                if low[neighbor] > discovery[node_id]:
                    bridges.add(edge_id)
                if parent_edge is not None and low[neighbor] >= discovery[node_id]:
                    articulation.add(node_id)
                steps.append(_step(
                    f"อัปเดต low({ _name(names, node_id) }) = {low[node_id]}",
                    node={node_id: "visited", neighbor: "consider"},
                    edge={edge_id: "tree"},
                ))
            else:
                low[node_id] = min(low[node_id], discovery[neighbor])
        if parent_edge is None and child_count > 1:
            articulation.add(node_id)

    for node_id in ids:
        if node_id not in discovery:
            components += 1
            visit(node_id, None)

    articulation_names = [_html(_name(names, node_id)) for node_id in ids if node_id in articulation]
    bridge_names = [
        _html(f"{_name(names, edge['u'])}–{_name(names, edge['v'])}")
        for edge in edges if edge["id"] in bridges
    ]
    steps.append(_step(
        f"พบ Articulation Point {len(articulation)} จุด และ Bridge {len(bridges)} เส้น",
        node={node_id: "consider" for node_id in articulation},
        edge={edge_id: "cut" for edge_id in bridges},
    ))
    summary = (
        f'<div class="hero">Articulation Point: <b>{", ".join(articulation_names) or "ไม่มี"}</b>'
        f'<br>Bridge: <b>{", ".join(bridge_names) or "ไม่มี"}</b>'
        f'<br>Connected Components: <b>{components}</b></div>'
    )
    return _result(
        "Bridge และ Articulation Point (DFS low-link)",
        "connectivity", steps, summary,
        articulationPoints=[node_id for node_id in ids if node_id in articulation],
        bridges=[edge["id"] for edge in edges if edge["id"] in bridges],
        components=components,
    )


def _minimum_cut_value(
    capacities: dict[tuple[int, int], float],
    nodes: list[int],
    source: int,
    sink: int,
    flow_limit: float | None = None,
) -> tuple[float, set[int]]:
    residual: dict[int, dict[int, float]] = {node_id: {} for node_id in nodes}
    for (u, v), capacity in capacities.items():
        residual.setdefault(u, {})[v] = residual.get(u, {}).get(v, 0.0) + capacity
        residual.setdefault(v, {})
    flow = 0.0
    while True:
        previous: dict[int, int | None] = {source: source}
        bottleneck: dict[int, float] = {source: math.inf}
        queue = deque([source])
        while queue and sink not in previous:
            current = queue.popleft()
            for neighbor, capacity in residual.get(current, {}).items():
                if capacity <= 1e-9 or neighbor in previous:
                    continue
                previous[neighbor] = current
                bottleneck[neighbor] = min(bottleneck[current], capacity)
                queue.append(neighbor)
        if sink not in previous:
            reachable = {source}
            queue = deque([source])
            while queue:
                current = queue.popleft()
                for neighbor, capacity in residual.get(current, {}).items():
                    if capacity > 1e-9 and neighbor not in reachable:
                        reachable.add(neighbor)
                        queue.append(neighbor)
            return flow, reachable
        current = sink
        augmentation = bottleneck[sink]
        while current != source:
            parent = previous[current]
            residual.setdefault(parent, {})[current] = residual.get(parent, {}).get(current, 0.0) - augmentation
            residual.setdefault(current, {})[parent] = residual.get(current, {}).get(parent, 0.0) + augmentation
            current = parent
        flow += augmentation
        if flow_limit is not None and flow >= flow_limit - 1e-9:
            return flow, set()


def _components_after_removal(
    ids: list[int],
    edges: list[dict[str, Any]],
    removed_vertices: set[int] | None = None,
    removed_edges: set[int] | None = None,
) -> list[list[int]]:
    removed_vertices = removed_vertices or set()
    removed_edges = removed_edges or set()
    adjacency = {node_id: [] for node_id in ids if node_id not in removed_vertices}
    for edge in edges:
        if edge["id"] in removed_edges or edge["u"] in removed_vertices or edge["v"] in removed_vertices:
            continue
        adjacency[edge["u"]].append(edge["v"])
        adjacency[edge["v"]].append(edge["u"])

    components: list[list[int]] = []
    visited: set[int] = set()
    for start in adjacency:
        if start in visited:
            continue
        component: list[int] = []
        queue = deque([start])
        visited.add(start)
        while queue:
            current = queue.popleft()
            component.append(current)
            for neighbor in adjacency[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        components.append(component)
    return components


def _vertex_connectivity(payload: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, names, directed = _graph(payload)
    ids = [node["id"] for node in nodes]
    if directed:
        raise ValueError("Vertex Connectivity ใช้กับกราฟไม่มีทิศทาง")
    if not ids:
        raise ValueError("ยังไม่มีจุดยอด")
    if any(edge["u"] == edge["v"] for edge in edges):
        raise ValueError("Vertex Connectivity ไม่รองรับ self-loop")

    if len(ids) > 100 or len(edges) > 5000:
        raise ValueError("Vertex Connectivity จำกัดที่ 100 จุดยอดและ 5,000 เส้น")

    adjacency: dict[int, set[int]] = {node_id: set() for node_id in ids}
    for edge in edges:
        adjacency[edge["u"]].add(edge["v"])
        adjacency[edge["v"]].add(edge["u"])
    initial_components = _components_after_removal(ids, edges)
    cut_vertices: set[int] = set()
    if len(ids) == 1 or len(initial_components) > 1:
        kappa = 0
    else:
        minimum_degree_vertex = min(ids, key=lambda node_id: len(adjacency[node_id]))
        kappa = len(adjacency[minimum_degree_vertex])
        cut_vertices = set(adjacency[minimum_degree_vertex])
        index = {node_id: position for position, node_id in enumerate(ids)}
        infinity = len(ids) + 1
        found_minimum = kappa <= 1
        for source_index, source in enumerate(ids):
            if found_minimum:
                break
            for sink in ids[source_index + 1:]:
                if sink in adjacency[source]:
                    continue
                capacities: dict[tuple[int, int], float] = {}
                for node_id, position in index.items():
                    capacity = infinity if node_id in (source, sink) else 1.0
                    capacities[(2 * position, 2 * position + 1)] = capacity
                for edge in edges:
                    u, v = index[edge["u"]], index[edge["v"]]
                    capacities[(2 * u + 1, 2 * v)] = infinity
                    capacities[(2 * v + 1, 2 * u)] = infinity
                cut_value, reachable = _minimum_cut_value(
                    capacities,
                    list(range(2 * len(ids))),
                    2 * index[source] + 1,
                    2 * index[sink],
                    flow_limit=float(kappa),
                )
                if int(cut_value) < kappa:
                    kappa = int(cut_value)
                    cut_vertices = {
                        node_id for node_id, position in index.items()
                        if node_id not in (source, sink)
                        and 2 * position in reachable
                        and 2 * position + 1 not in reachable
                    }
                    if kappa <= 1:
                        found_minimum = True
                        break
    remaining_components = _components_after_removal(ids, edges, removed_vertices=cut_vertices)
    cut_names = [_name(names, node_id) for node_id in ids if node_id in cut_vertices]
    component_text = " | ".join(
        "{" + ", ".join(_html(_name(names, node_id)) for node_id in component) + "}"
        for component in remaining_components
    ) or "ไม่มีจุดยอดเหลือ"
    if kappa == 0:
        steps = [_step(
            "กราฟไม่เชื่อมต่ออยู่แล้ว จึงไม่ต้องตัดจุดยอดเพิ่ม"
            if len(ids) > 1 else "มีจุดยอดเดียว ไม่มีชุดตัดที่จำเป็น"
        )]
        cut_description = "ไม่ต้องตัดจุดยอด — กราฟไม่เชื่อมต่ออยู่แล้ว" if len(ids) > 1 else "ไม่มี (กราฟมีจุดยอดเดียว)"
    else:
        steps = [_step(
            f"ตัดจุดยอด {', '.join(cut_names)} แล้วกราฟแยกเป็น {len(remaining_components)} components",
            node={node_id: "consider" for node_id in cut_vertices},
        )]
        cut_description = ", ".join(_html(name) for name in cut_names)
    summary = (
        f'<div class="hero">Vertex Connectivity κ(G) = <b>{_fmt(kappa)}</b></div>'
        f'<div class="note"><b>จุดยอดที่ต้องตัด ({len(cut_vertices)}):</b> {cut_description}'
        f'<br><b>หลังตัดแล้วเหลือ:</b> {component_text}</div>'
    )
    return _result(
        "Vertex Connectivity κ(G)", "vertexConnectivity",
        steps, summary,
        kappa=kappa, cutVertices=[node_id for node_id in ids if node_id in cut_vertices],
        componentsAfterRemoval=remaining_components,
    )


def _edge_connectivity(payload: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, names, directed = _graph(payload)
    ids = [node["id"] for node in nodes]
    if directed:
        raise ValueError("Edge Connectivity ใช้กับกราฟไม่มีทิศทาง")
    if not ids:
        raise ValueError("ยังไม่มีจุดยอด")

    if len(ids) > 100 or len(edges) > 5000:
        raise ValueError("Edge Connectivity จำกัดที่ 100 จุดยอดและ 5,000 เส้น")

    initial_components = _components_after_removal(ids, edges)
    cut_edges: set[int] = set()
    best_partition: set[int] = set()
    if len(ids) == 1 or len(initial_components) > 1:
        lambda_value = 0
    else:
        capacities: dict[tuple[int, int], float] = {}
        for edge in edges:
            if edge["u"] == edge["v"]:
                continue
            pair = (edge["u"], edge["v"])
            reverse_pair = (edge["v"], edge["u"])
            capacities[pair] = capacities.get(pair, 0.0) + 1.0
            capacities[reverse_pair] = capacities.get(reverse_pair, 0.0) + 1.0
        root = ids[0]
        lambda_value = len(edges) + 1
        for sink in ids[1:]:
            cut_value, reachable = _minimum_cut_value(capacities, ids, root, sink)
            if int(cut_value) < lambda_value:
                lambda_value = int(cut_value)
                best_partition = reachable
        cut_edges = {
            edge["id"] for edge in edges
            if edge["u"] != edge["v"]
            and ((edge["u"] in best_partition) != (edge["v"] in best_partition))
        }
    remaining_components = _components_after_removal(ids, edges, removed_edges=cut_edges)
    cut_names = [
        f'{_name(names, edge["u"])}–{_name(names, edge["v"])}'
        for edge in edges if edge["id"] in cut_edges
    ]
    component_text = " | ".join(
        "{" + ", ".join(_html(_name(names, node_id)) for node_id in component) + "}"
        for component in remaining_components
    ) or "ไม่มีจุดยอดเหลือ"
    if lambda_value == 0:
        steps = [_step(
            "กราฟไม่เชื่อมต่ออยู่แล้ว จึงไม่ต้องตัดเส้นเชื่อมเพิ่ม"
            if len(ids) > 1 else "มีจุดยอดเดียว ไม่มีชุดตัดที่จำเป็น"
        )]
        cut_description = "ไม่ต้องตัดเส้นเชื่อม — กราฟไม่เชื่อมต่ออยู่แล้ว" if len(ids) > 1 else "ไม่มี (กราฟมีจุดยอดเดียว)"
    else:
        steps = [_step(
            f"ตัดเส้นเชื่อม {', '.join(cut_names)} แล้วกราฟแยกเป็น {len(remaining_components)} components",
            edge={edge_id: "cut" for edge_id in cut_edges},
        )]
        cut_description = ", ".join(_html(name) for name in cut_names)
    summary = (
        f'<div class="hero">Edge Connectivity λ(G) = <b>{_fmt(lambda_value)}</b></div>'
        f'<div class="note"><b>เส้นเชื่อมที่ต้องตัด ({len(cut_edges)}):</b> {cut_description}'
        f'<br><b>หลังตัดแล้วเหลือ:</b> {component_text}</div>'
    )
    return _result(
        "Edge Connectivity λ(G)", "edgeConnectivity",
        steps, summary,
        lambdaValue=lambda_value, cutEdges=[edge["id"] for edge in edges if edge["id"] in cut_edges],
        componentsAfterRemoval=remaining_components,
    )


def _maximum_bipartite_matching(payload: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, names, directed = _graph(payload)
    ids = [node["id"] for node in nodes]
    if directed:
        raise ValueError("Maximum Bipartite Matching ใช้กับกราฟไม่มีทิศทาง")
    if len(ids) > 800 or len(edges) > 10000:
        raise ValueError("Matching จำกัดที่ 800 จุดยอดและ 10,000 เส้น")

    adjacency: dict[int, dict[int, int]] = {node_id: {} for node_id in ids}
    for edge in edges:
        u, v = edge["u"], edge["v"]
        if u == v:
            raise ValueError("กราฟที่มี Self-loop ไม่เป็น Bipartite")
        adjacency[u][v] = min(edge["id"], adjacency[u].get(v, edge["id"]))
        adjacency[v][u] = min(edge["id"], adjacency[v].get(u, edge["id"]))

    side: dict[int, int] = {}
    for start in ids:
        if start in side:
            continue
        side[start] = 0
        queue = deque([start])
        while queue:
            current = queue.popleft()
            for neighbor in adjacency[current]:
                if neighbor not in side:
                    side[neighbor] = 1 - side[current]
                    queue.append(neighbor)
                elif side[neighbor] == side[current]:
                    raise ValueError("กราฟนี้ไม่เป็น Bipartite จึงหา Bipartite Matching ไม่ได้")

    left = [node_id for node_id in ids if side[node_id] == 0]
    match_left: dict[int, int] = {}
    match_right: dict[int, int] = {}
    distance: dict[int, int] = {}
    infinity = len(ids) + 1
    shortest_path = infinity
    steps: list[dict[str, Any]] = [
        _step(
            f"ตรวจ Bipartite ผ่าน: ฝั่งซ้าย {len(left)} จุด; เริ่ม Hopcroft–Karp"
        )
    ]

    def build_layers() -> bool:
        nonlocal shortest_path
        queue = deque()
        for node_id in left:
            if node_id not in match_left:
                distance[node_id] = 0
                queue.append(node_id)
            else:
                distance[node_id] = infinity
        found_augmenting_path = False
        shortest_path = infinity
        while queue:
            current = queue.popleft()
            if distance[current] >= shortest_path:
                continue
            for neighbor in adjacency[current]:
                paired_left = match_right.get(neighbor)
                if paired_left is None:
                    found_augmenting_path = True
                    shortest_path = distance[current] + 1
                elif distance[paired_left] == infinity:
                    distance[paired_left] = distance[current] + 1
                    queue.append(paired_left)
        return found_augmenting_path and shortest_path < infinity

    def augment(current: int) -> bool:
        for neighbor in adjacency[current]:
            paired_left = match_right.get(neighbor)
            if (
                paired_left is None
                and distance[current] + 1 == shortest_path
            ) or (
                paired_left is not None
                and distance.get(paired_left) == distance[current] + 1
                and augment(paired_left)
            ):
                match_left[current] = neighbor
                match_right[neighbor] = current
                return True
        distance[current] = infinity
        return False

    while build_layers():
        for node_id in left:
            if node_id not in match_left and augment(node_id):
                matched_edge_ids = [
                    adjacency[left_node][right_node]
                    for left_node, right_node in match_left.items()
                ]
                steps.append(_step(
                    f"เพิ่มคู่จับคู่ผ่าน {_name(names, node_id)}; ขนาด Matching = {len(match_left)}",
                    node={node_id: "visited", **{right: "visited" for right in match_left.values()}},
                    edge={edge_id: "tree" for edge_id in matched_edge_ids},
                ))

    pairs = [
        {"left": left_id, "right": right_id}
        for left_id, right_id in match_left.items()
    ]
    matched_edges = [adjacency[pair["left"]][pair["right"]] for pair in pairs]
    reachable_left = {node_id for node_id in left if node_id not in match_left}
    reachable_right: set[int] = set()
    queue = deque(reachable_left)
    while queue:
        left_node = queue.popleft()
        for right_node in adjacency[left_node]:
            if match_left.get(left_node) == right_node or right_node in reachable_right:
                continue
            reachable_right.add(right_node)
            paired_left = match_right.get(right_node)
            if paired_left is not None and paired_left not in reachable_left:
                reachable_left.add(paired_left)
                queue.append(paired_left)

    cover_left = [node_id for node_id in left if node_id not in reachable_left]
    cover_right = [node_id for node_id in ids if side[node_id] == 1 and node_id in reachable_right]
    minimum_vertex_cover = cover_left + cover_right
    cover_edges = [
        edge["id"]
        for edge in edges
        if edge["u"] in minimum_vertex_cover or edge["v"] in minimum_vertex_cover
    ]
    steps.append(_step(
        f"Konig: minimum vertex cover มี {len(minimum_vertex_cover)} จุด เท่ากับ Matching",
        node={node_id: "consider" for node_id in minimum_vertex_cover},
        edge={edge_id: "tree" for edge_id in cover_edges},
    ))
    display_pairs = ", ".join(
        f"{_html(_name(names, pair['left']))}–{_html(_name(names, pair['right']))}"
        for pair in pairs
    )
    display_cover = ", ".join(
        _html(_name(names, node_id)) for node_id in minimum_vertex_cover
    )
    hall_note = (
        "มี matching ที่จับคู่ฝั่งซ้ายได้ครบ; ตาม Hall ทุกชุด S ของฝั่งซ้ายมี |N(S)| ≥ |S|"
        if len(pairs) == len(left)
        else "Matching จับคู่ฝั่งซ้ายได้ไม่ครบ; ตาม Hall มีชุด S ของฝั่งซ้ายที่ |N(S)| < |S|"
    )
    summary = (
        f'<div class="hero">Maximum Matching มี <b>{len(pairs)}</b> คู่'
        f'<br>{display_pairs or "ไม่มีคู่ที่จับได้"}'
        f'<br>Minimum Vertex Cover (Konig): <b>{len(minimum_vertex_cover)}</b> จุด'
        f'<br>{display_cover or "ไม่มีจุดยอด"}'
        f'<br><small>{_html(hall_note)}</small></div>'
    )
    return _result(
        "Maximum Bipartite Matching (Hopcroft–Karp)",
        "matching", steps, summary,
        pairs=pairs, matchedEdges=matched_edges,
        size=len(pairs),
        left=[node_id for node_id in ids if side[node_id] == 0],
        right=[node_id for node_id in ids if side[node_id] == 1],
        minimumVertexCover=minimum_vertex_cover,
        coverEdges=cover_edges,
    )


def _hungarian_assignment(payload: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, names, directed = _graph(payload)
    ids = [node["id"] for node in nodes]
    if directed:
        raise ValueError("Hungarian Algorithm ใช้กับกราฟไม่มีทิศทาง")
    if not ids:
        raise ValueError("ยังไม่มีจุดยอด")
    if len(ids) > 100 or len(edges) > 5000:
        raise ValueError("Hungarian Algorithm จำกัดที่ 100 จุดยอดและ 5,000 เส้น")

    side: dict[int, int] = {}
    adjacency: dict[int, list[int]] = {node_id: [] for node_id in ids}
    for edge in edges:
        u, v = edge["u"], edge["v"]
        if u == v:
            raise ValueError("Assignment Problem ไม่รองรับ Self-loop")
        adjacency[u].append(v)
        adjacency[v].append(u)

    for start in ids:
        if start in side:
            continue
        side[start] = 0
        queue = deque([start])
        while queue:
            current = queue.popleft()
            for neighbor in adjacency[current]:
                if neighbor not in side:
                    side[neighbor] = 1 - side[current]
                    queue.append(neighbor)
                elif side[neighbor] == side[current]:
                    raise ValueError("Assignment Problem ต้องเป็นกราฟ Bipartite")

    left = [node_id for node_id in ids if side[node_id] == 0]
    right = [node_id for node_id in ids if side[node_id] == 1]
    if not left or not right:
        raise ValueError("Assignment Problem ต้องมีจุดยอดทั้งสองฝั่ง")

    costs: dict[tuple[int, int], tuple[float, int]] = {}
    for edge in edges:
        left_id, right_id = (
            (edge["u"], edge["v"])
            if side[edge["u"]] == 0
            else (edge["v"], edge["u"])
        )
        pair = (left_id, right_id)
        current = costs.get(pair)
        if current is None or edge["w"] < current[0]:
            costs[pair] = (float(edge["w"]), edge["id"])

    transposed = len(left) > len(right)
    rows, columns = (right, left) if transposed else (left, right)

    def cost_for(row_id: int, column_id: int) -> float:
        pair = (column_id, row_id) if transposed else (row_id, column_id)
        value = costs.get(pair)
        return value[0] if value is not None else math.inf

    row_count, column_count = len(rows), len(columns)
    potentials_rows = [0.0] * (row_count + 1)
    potentials_columns = [0.0] * (column_count + 1)
    column_match = [0] * (column_count + 1)
    predecessor = [0] * (column_count + 1)
    steps = [
        _step(
            f"แบ่งกราฟ Bipartite ได้ {len(left)} จุดฝั่งซ้าย และ {len(right)} จุดฝั่งขวา; "
            "หา Assignment ต้นทุนต่ำสุด โดยเส้นที่ไม่มีอยู่ถือว่าเลือกไม่ได้"
        )
    ]

    for row_index in range(1, row_count + 1):
        column_match[0] = row_index
        current_column = 0
        min_reduced_cost = [math.inf] * (column_count + 1)
        used = [False] * (column_count + 1)
        while True:
            used[current_column] = True
            current_row = column_match[current_column]
            delta = math.inf
            next_column = 0
            for column_index in range(1, column_count + 1):
                if used[column_index]:
                    continue
                reduced_cost = (
                    cost_for(rows[current_row - 1], columns[column_index - 1])
                    - potentials_rows[current_row]
                    - potentials_columns[column_index]
                )
                if reduced_cost < min_reduced_cost[column_index]:
                    min_reduced_cost[column_index] = reduced_cost
                    predecessor[column_index] = current_column
                if min_reduced_cost[column_index] < delta:
                    delta = min_reduced_cost[column_index]
                    next_column = column_index
            if math.isinf(delta):
                raise ValueError(
                    "ไม่มี Assignment ครบทุกจุดของฝั่งที่มีขนาดเล็กกว่า "
                    "โปรดตรวจว่ามีเส้นเชื่อมที่เลือกได้เพียงพอ"
                )
            for column_index in range(column_count + 1):
                if used[column_index]:
                    potentials_rows[column_match[column_index]] += delta
                    potentials_columns[column_index] -= delta
                else:
                    min_reduced_cost[column_index] -= delta
            current_column = next_column
            if column_match[current_column] == 0:
                break
        while True:
            previous_column = predecessor[current_column]
            column_match[current_column] = column_match[previous_column]
            current_column = previous_column
            if current_column == 0:
                break

        assignment = {
            rows[column_match[column] - 1]: columns[column - 1]
            for column in range(1, column_count + 1)
            if column_match[column] != 0
        }
        assignment_pairs = [
            (row_id, column_id) if not transposed else (column_id, row_id)
            for row_id, column_id in assignment.items()
        ]
        assignment_edge_ids = [
            costs[pair][1]
            for pair in assignment_pairs
            if pair in costs
        ]
        assigned_names = ", ".join(
            f"{_html(_name(names, left_id))}–{_html(_name(names, right_id))}"
            for left_id, right_id in assignment_pairs
        )
        steps.append(_step(
            f"เพิ่ม Assignment สำหรับ {_html(_name(names, rows[row_index - 1]))}; "
            f"จับคู่แล้ว {len(assignment_pairs)} คู่: {assigned_names}",
            node={
                node_id: "visited"
                for pair in assignment_pairs
                for node_id in pair
            },
            edge={edge_id: "tree" for edge_id in assignment_edge_ids},
        ))

    final_pairs = [
        (rows[column_match[column] - 1], columns[column - 1])
        for column in range(1, column_count + 1)
        if column_match[column] != 0
    ]
    pairs = [
        {
            "left": row_id if not transposed else column_id,
            "right": column_id if not transposed else row_id,
            "cost": costs[(row_id, column_id) if not transposed else (column_id, row_id)][0],
            "edge": costs[(row_id, column_id) if not transposed else (column_id, row_id)][1],
        }
        for row_id, column_id in final_pairs
    ]
    total_cost = sum(pair["cost"] for pair in pairs)
    pair_text = ", ".join(
        f"{_html(_name(names, pair['left']))}–{_html(_name(names, pair['right']))} "
        f"(cost {_fmt(pair['cost'])})"
        for pair in pairs
    )
    steps.append(_step(
        f"ผล Assignment ครบ {len(pairs)} คู่; ต้นทุนรวม = {_fmt(total_cost)}",
        node={node_id: "visited" for pair in pairs for node_id in (pair["left"], pair["right"])},
        edge={pair["edge"]: "tree" for pair in pairs},
    ))
    summary = (
        f'<div class="hero">ต้นทุน Assignment ต่ำสุด: <b>{_fmt(total_cost)}</b>'
        f'<br>{pair_text}</div>'
    )
    return _result(
        "Hungarian Algorithm (Minimum-Cost Assignment)",
        "assignment", steps, summary,
        pairs=pairs, size=len(pairs), total=total_cost,
        matchedEdges=[pair["edge"] for pair in pairs],
        left=left, right=right,
    )


def _tsp(payload: dict[str, Any], mode: str) -> dict[str, Any]:
    nodes, edges, names, directed = _graph(payload)
    ids = [node["id"] for node in nodes]
    if not ids:
        raise ValueError("ยังไม่มีจุดยอด")
    limit = 10 if mode == "exact" else 250
    if len(ids) > limit:
        raise ValueError(f"TSP {mode} จำกัดที่ {limit} จุดยอด")

    weight: dict[tuple[int, int], tuple[float, int]] = {}
    for edge in edges:
        pair = (edge["u"], edge["v"])
        current = weight.get(pair)
        if current is None or edge["w"] < current[0]:
            weight[pair] = (edge["w"], edge["id"])
        if not directed:
            reverse = (edge["v"], edge["u"])
            current = weight.get(reverse)
            if current is None or edge["w"] < current[0]:
                weight[reverse] = (edge["w"], edge["id"])

    start = ids[0]

    def route_cost(route: list[int]) -> float | None:
        if len(ids) == 1:
            return 0.0
        total = 0.0
        for u, v in zip(route, route[1:]):
            arc = weight.get((u, v))
            if arc is None:
                return None
            total += arc[0]
        return total

    def route_edges(route: list[int]) -> list[int]:
        return [weight[(u, v)][1] for u, v in zip(route, route[1:])]

    steps: list[dict[str, Any]] = [
        _step(f"TSP เริ่มจาก {_name(names, start)}; หา Hamiltonian Cycle กลับมาจุดเริ่ม")
    ]
    route: list[int] | None = None

    if mode == "exact":
        if len(ids) == 1:
            route = [start, start]
        else:
            others = ids[1:]
            count = len(others)
            full_mask = (1 << count) - 1
            dp: dict[tuple[int, int], float] = {}
            parent: dict[tuple[int, int], int | None] = {}
            for index, node_id in enumerate(others):
                arc = weight.get((start, node_id))
                if arc is not None:
                    mask = 1 << index
                    dp[(mask, index)] = arc[0]
                    parent[(mask, index)] = None

            for mask in range(1, full_mask + 1):
                if mask.bit_count() <= 1:
                    continue
                changed = 0
                for last in range(count):
                    bit = 1 << last
                    if not mask & bit:
                        continue
                    previous_mask = mask ^ bit
                    best: float | None = None
                    best_previous: int | None = None
                    for previous in range(count):
                        previous_cost = dp.get((previous_mask, previous))
                        arc = weight.get((others[previous], others[last]))
                        if previous_cost is None or arc is None:
                            continue
                        candidate = previous_cost + arc[0]
                        if best is None or candidate < best:
                            best = candidate
                            best_previous = previous
                    if best is not None:
                        dp[(mask, last)] = best
                        parent[(mask, last)] = best_previous
                        changed += 1
                if changed:
                    steps.append(_step(
                        f"Held–Karp: ประมวลผลชุดที่มี {mask.bit_count()} จุดกลาง "
                        f"({changed} สถานะที่เข้าถึงได้)",
                    ))

            best_total: float | None = None
            best_last: int | None = None
            for last in range(count):
                path_cost = dp.get((full_mask, last))
                closing = weight.get((others[last], start))
                if path_cost is None or closing is None:
                    continue
                candidate = path_cost + closing[0]
                if best_total is None or candidate < best_total:
                    best_total = candidate
                    best_last = last
            if best_last is not None:
                reverse_path = [best_last]
                mask = full_mask
                current = best_last
                while parent[(mask, current)] is not None:
                    previous = parent[(mask, current)]
                    mask ^= 1 << current
                    current = previous
                    reverse_path.append(current)
                route = [start] + [others[index] for index in reversed(reverse_path)] + [start]
    else:
        route = [start]
        unvisited = set(ids[1:])
        while unvisited:
            current = route[-1]
            candidates = [
                (weight[(current, target)][0], ids.index(target), target)
                for target in unvisited if (current, target) in weight
            ]
            if not candidates:
                route = None
                break
            _, _, target = min(candidates)
            route.append(target)
            unvisited.remove(target)
            edge_id = weight[(current, target)][1]
            steps.append(_step(
                f"เลือกเส้นทางราคาต่ำสุดจาก {_name(names, current)} ไป {_name(names, target)}",
                node={current: "visited", target: "current"},
                edge={edge_id: "consider"},
            ))
        if route is not None and (route[-1], start) in weight:
            route.append(start)
        else:
            route = None

        if mode == "2opt" and route is not None:
            improved = True
            while improved:
                improved = False
                current_cost = route_cost(route)
                if current_cost is None:
                    break
                for left_index in range(1, len(route) - 2):
                    for right_index in range(left_index + 1, len(route) - 1):
                        candidate_route = (
                            route[:left_index]
                            + list(reversed(route[left_index:right_index + 1]))
                            + route[right_index + 1:]
                        )
                        candidate_cost = route_cost(candidate_route)
                        if candidate_cost is not None and candidate_cost < current_cost - 1e-12:
                            route = candidate_route
                            improved = True
                            steps.append(_step(
                                f"2-opt: ปรับลำดับเส้นทาง ลดน้ำหนักรวมเหลือ {_fmt(candidate_cost)}",
                                node={node_id: "visited" for node_id in route[:-1]},
                                edge={edge_id: "tree" for edge_id in route_edges(route)},
                            ))
                            break
                    if improved:
                        break

    if route is None:
        return _result(
            "TSP — " + ("Held–Karp" if mode == "exact" else "Nearest Neighbor" if mode == "nearest" else "2-opt"),
            "tsp", steps,
            '<div class="hero warn">ไม่พบ Hamiltonian Cycle จากจุดเริ่มที่เลือก</div>',
            exists=False,
        )

    total = route_cost(route)
    if total is None:
        return _result("TSP", "tsp", steps, '<div class="hero warn">เส้นทางไม่สมบูรณ์</div>', exists=False)
    selected_edges = route_edges(route)
    steps.append(_step(
        f"เส้นทาง: {' → '.join(_name(names, node_id) for node_id in route)}; น้ำหนักรวม = {_fmt(total)}",
        node={node_id: "path" for node_id in set(route)},
        edge={edge_id: "path" for edge_id in selected_edges},
    ))
    route_text = " → ".join(_html(_name(names, node_id)) for node_id in route)
    mode_name = {"exact": "Held–Karp DP", "nearest": "Nearest Neighbor", "2opt": "Nearest Neighbor + 2-opt"}[mode]
    summary = (
        f'<div class="hero">{_html(mode_name)}<br>น้ำหนักรวม: <b>{_fmt(total)}</b>'
        f'<br>{route_text}</div>'
    )
    return _result(
        f"TSP — {mode_name}", "tsp", steps, summary,
        exists=True, route=route, edgeOrder=selected_edges, total=total,
        optimal=(mode == "exact"),
    )


def _prufer_decode(payload: dict[str, Any]) -> dict[str, Any]:
    code = payload.get("code")
    if not isinstance(code, list) or any(
        isinstance(value, bool) or not isinstance(value, int) for value in code
    ):
        raise ValueError("Prüfer Code ต้องเป็นรายการจำนวนเต็ม")
    count = len(code) + 2
    if count > 5000:
        raise ValueError("Prüfer Decode จำกัดที่ 5,000 จุดยอด")
    if any(value < 1 or value > count for value in code):
        raise ValueError(f"สมาชิก Prüfer Code ต้องอยู่ระหว่าง 1 ถึง {count}")

    degree = [0] + [1] * count
    for value in code:
        degree[value] += 1
    leaves = [node_id for node_id in range(1, count + 1) if degree[node_id] == 1]
    heapq.heapify(leaves)
    edges: list[dict[str, int]] = []
    steps: list[dict[str, Any]] = [_step(f"ถอดรหัส Prüfer Code {code}; มี {count} จุดยอด")]
    for value in code:
        leaf = heapq.heappop(leaves)
        edges.append({"id": len(edges) + 1, "u": leaf, "v": value, "w": 1})
        degree[leaf] -= 1
        degree[value] -= 1
        if degree[value] == 1:
            heapq.heappush(leaves, value)
        steps.append(_step(
            f"เชื่อมใบ {leaf} กับ {value}",
            node={leaf: "consider", value: "visited"},
            edge={edges[-1]["id"]: "tree"},
        ))
    remaining = [node_id for node_id in range(1, count + 1) if degree[node_id] == 1]
    if len(remaining) != 2:
        raise ValueError("Prüfer Code ไม่สามารถถอดรหัสเป็นต้นไม้ได้")
    edges.append({"id": len(edges) + 1, "u": remaining[0], "v": remaining[1], "w": 1})
    steps.append(_step(
        f"เชื่อมสองใบสุดท้าย {remaining[0]}–{remaining[1]}",
        node={node_id: "path" for node_id in remaining},
        edge={edges[-1]["id"]: "tree"},
    ))
    summary = (
        f'<div class="hero">ถอดรหัสเป็นต้นไม้ <b>{count}</b> จุดยอด '
        f'และ <b>{len(edges)}</b> เส้น</div>'
    )
    return _result(
        "Prüfer Code Decode", "pruferDecode", steps, summary,
        nodes=[{"id": node_id, "label": f"v{node_id}"} for node_id in range(1, count + 1)],
        edges=edges,
    )


def _havel_hakimi(payload: dict[str, Any]) -> dict[str, Any]:
    sequence = payload.get("degreeSequence")
    if not isinstance(sequence, list) or any(
        isinstance(value, bool) or not isinstance(value, int) for value in sequence
    ):
        raise ValueError("Degree Sequence ต้องเป็นรายการจำนวนเต็ม")
    count = len(sequence)
    if not 1 <= count <= 500:
        raise ValueError("Degree Sequence ต้องมีจุดยอด 1–500 จุด")
    if any(value < 0 for value in sequence):
        raise ValueError("Degree ต้องไม่ติดลบ")
    if any(value >= count for value in sequence):
        raise ValueError("Degree ของ Simple Graph ต้องน้อยกว่าจำนวนจุดยอด")

    ordered_degrees = sorted(sequence, reverse=True)
    prefix = [0]
    for degree in ordered_degrees:
        prefix.append(prefix[-1] + degree)
    witness = next(
        (
            k for k in range(1, count + 1)
            if prefix[k] > k * (k - 1) + sum(min(degree, k) for degree in ordered_degrees[k:])
        ),
        None,
    )
    if sum(sequence) % 2:
        summary = '<div class="hero warn">สร้างกราฟอย่างง่ายไม่ได้: ผลรวม Degree เป็นจำนวนคี่</div>'
        return _result("Havel–Hakimi / Erdős–Gallai", "degreeSequence", [_step("ผลรวม degree ต้องเป็นจำนวนคู่")], summary, exists=False, graphical=False, witness=None)
    if witness is not None:
        summary = (
            f'<div class="hero warn">สร้างกราฟอย่างง่ายไม่ได้: Erdős–Gallai ไม่ผ่านเมื่อ k={witness}'
            f'<br>{prefix[witness]} &gt; {witness * (witness - 1) + sum(min(degree, witness) for degree in ordered_degrees[witness:])}</div>'
        )
        return _result(
            "Havel–Hakimi / Erdős–Gallai", "degreeSequence",
            [_step(f"Erdős–Gallai ไม่ผ่านที่ k={witness}")],
            summary, exists=False, graphical=False, witness=witness,
        )

    remaining = [[degree, node_id] for node_id, degree in enumerate(sequence, start=1)]
    graph_edges: list[dict[str, int]] = []
    steps: list[dict[str, Any]] = [_step("เริ่ม Havel–Hakimi: เรียง degree จากมากไปน้อย")]
    while True:
        remaining.sort(key=lambda item: (-item[0], item[1]))
        if not remaining or remaining[0][0] == 0:
            break
        degree, source = remaining.pop(0)
        if degree > len(remaining):
            raise ValueError("Erdős–Gallai ผ่านแต่ Havel–Hakimi สร้างกราฟไม่สำเร็จ")
        for index in range(degree):
            remaining[index][0] -= 1
            if remaining[index][0] < 0:
                raise ValueError("Erdős–Gallai ผ่านแต่ Havel–Hakimi สร้างกราฟไม่สำเร็จ")
            target = remaining[index][1]
            graph_edges.append({
                "id": len(graph_edges) + 1,
                "u": source,
                "v": target,
                "w": 1,
            })
        steps.append(_step(
            f"เชื่อม v{source} กับ {', '.join(f'v{remaining[index][1]}' for index in range(degree))}",
            node={source: "current", **{remaining[index][1]: "visited" for index in range(degree)}},
            edge={edge["id"]: "tree" for edge in graph_edges[-degree:]},
        ))

    actual_degrees = {node_id: 0 for node_id in range(1, count + 1)}
    for edge in graph_edges:
        actual_degrees[edge["u"]] += 1
        actual_degrees[edge["v"]] += 1
    if sorted(actual_degrees.values(), reverse=True) != ordered_degrees:
        raise ValueError("Havel–Hakimi ผลลัพธ์ไม่ตรงกับ Degree Sequence ที่ให้มา")

    summary = (
        f'<div class="hero">Degree Sequence เป็นกราฟิกตาม Erdős–Gallai'
        f'<br>สร้างกราฟได้ {count} จุดยอด และ {len(graph_edges)} เส้น</div>'
    )
    return _result(
        "Havel–Hakimi Graph Construction",
        "degreeSequence", steps, summary,
        exists=True, graphical=True, witness=None,
        nodes=[{"id": node_id, "label": f"v{node_id}"} for node_id in range(1, count + 1)],
        edges=graph_edges,
    )


def _hamiltonian(payload: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, names, directed = _graph(payload)
    ids = [node["id"] for node in nodes]
    count = len(ids)
    if not ids:
        raise ValueError("ยังไม่มีจุดยอด")
    if count > 15:
        raise ValueError("Hamiltonian Exact จำกัดที่ 15 จุดยอด")

    adjacency: dict[int, set[int]] = {node_id: set() for node_id in ids}
    edge_for: dict[tuple[int, int], int] = {}
    for edge in edges:
        u, v = edge["u"], edge["v"]
        if u == v:
            continue
        adjacency[u].add(v)
        edge_for.setdefault((u, v), edge["id"])
        if not directed:
            adjacency[v].add(u)
            edge_for.setdefault((v, u), edge["id"])

    degrees = {node_id: len(adjacency[node_id]) for node_id in ids}
    dirac = not directed and count >= 3 and all(degrees[node_id] >= count / 2 for node_id in ids)
    ore = not directed and count >= 3 and all(
        degrees[u] + degrees[v] >= count
        for index, u in enumerate(ids)
        for v in ids[index + 1:]
        if v not in adjacency[u]
    )

    search_limit = 500_000
    searches = 0
    complete = True

    def find_cycle() -> list[int] | None:
        nonlocal searches, complete
        start = ids[0]
        path = [start]
        visited = {start}

        def visit(current: int) -> list[int] | None:
            nonlocal searches, complete
            searches += 1
            if searches > search_limit:
                complete = False
                return None
            if len(path) == count:
                return path.copy() if start in adjacency[current] else None
            candidates = sorted(
                (neighbor for neighbor in adjacency[current] if neighbor not in visited),
                key=lambda node_id: len(adjacency[node_id]),
            )
            for neighbor in candidates:
                visited.add(neighbor)
                path.append(neighbor)
                result = visit(neighbor)
                if result:
                    return result
                path.pop()
                visited.remove(neighbor)
                if not complete:
                    return None
            return None

        return visit(start)

    def find_path() -> list[int] | None:
        nonlocal searches, complete
        starts = sorted(ids, key=lambda node_id: len(adjacency[node_id]))
        for start in starts:
            path = [start]
            visited = {start}

            def visit(current: int) -> list[int] | None:
                nonlocal searches, complete
                searches += 1
                if searches > search_limit:
                    complete = False
                    return None
                if len(path) == count:
                    return path.copy()
                candidates = sorted(
                    (neighbor for neighbor in adjacency[current] if neighbor not in visited),
                    key=lambda node_id: len(adjacency[node_id]),
                )
                for neighbor in candidates:
                    visited.add(neighbor)
                    path.append(neighbor)
                    result = visit(neighbor)
                    if result:
                        return result
                    path.pop()
                    visited.remove(neighbor)
                    if not complete:
                        return None
                return None

            result = visit(start)
            if result:
                return result
            if not complete:
                return None
        return None

    cycle = find_cycle() if count >= 3 else None
    route = cycle if cycle is not None else (find_path() if complete else None)
    is_cycle = cycle is not None
    if count == 1:
        route = [ids[0]]
    if route is None:
        message = (
            "หยุดเมื่อถึงขีดจำกัดการค้นหา; ผลนี้ยังสรุปว่าไม่มี Hamiltonian Path/Cycle ไม่ได้"
            if not complete
            else "ตรวจครบแล้ว: ไม่มี Hamiltonian Path/Cycle"
        )
        summary = f'<div class="hero warn">{message}</div>'
        steps = [_step(f"DFS Backtracking ตรวจ {searches:,} สถานะ")]
        return _result(
            "Hamiltonian Path / Cycle", "hamiltonian", steps, summary,
            exists=False, complete=complete, searchStates=min(searches, search_limit),
            dirac=dirac, ore=ore,
        )

    route_edges = [
        edge_for[(u, v)]
        for u, v in zip(route, route[1:])
    ]
    if is_cycle:
        route_edges.append(edge_for[(route[-1], route[0])])
    kind = "Hamiltonian Cycle" if is_cycle else "Hamiltonian Path"
    route_text = " → ".join(_html(_name(names, node_id)) for node_id in route)
    if is_cycle:
        route_text += f" → {_html(_name(names, route[0]))}"
    theorem = (
        f'<p>Dirac sufficient condition: {"ผ่าน" if dirac else "ไม่ผ่าน"}; '
        f'Ore sufficient condition: {"ผ่าน" if ore else "ไม่ผ่าน"}.</p>'
        if not directed and count >= 3 else ""
    )
    summary = (
        f'<div class="hero">พบ <b>{kind}</b><br>{route_text}'
        f'<br>จำนวนสถานะค้นหา: {searches:,}</div>{theorem}'
    )
    steps = [
        _step(f"DFS Backtracking: ทดลอง {_name(names, node_id)}", node={node_id: "visited"})
        for node_id in route
    ]
    steps.append(_step(
        f"พบ {kind}",
        node={node_id: "path" for node_id in route},
        edge={edge_id: "path" for edge_id in route_edges},
    ))
    return _result(
        "Hamiltonian Path / Cycle", "hamiltonian", steps, summary,
        exists=True, complete=True, cycle=is_cycle, route=route,
        edgeOrder=route_edges, searchStates=searches, dirac=dirac, ore=ore,
    )


def _graph_transform(payload: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, names, directed = _graph(payload)
    operation = payload.get("operation")
    if operation == "complement":
        if directed:
            raise ValueError("Complement รองรับกราฟไม่มีทิศทาง")
        pairs = set()
        for edge in edges:
            if edge["u"] == edge["v"]:
                raise ValueError("Complement ต้องใช้กราฟอย่างง่ายที่ไม่มี Self-loop")
            pair = (min(edge["u"], edge["v"]), max(edge["u"], edge["v"]))
            if pair in pairs:
                raise ValueError("Complement ต้องใช้กราฟอย่างง่ายที่ไม่มีเส้นขนาน")
            pairs.add(pair)
        new_edges = []
        edge_id = 1
        for index, node in enumerate(nodes):
            for other in nodes[index + 1:]:
                u, v = node["id"], other["id"]
                if (min(u, v), max(u, v)) not in pairs:
                    new_edges.append({"id": edge_id, "u": u, "v": v, "w": 1})
                    edge_id += 1
        title = "Complement Graph"
        message = f"สร้าง Complement: มี {len(nodes)} จุด และ {len(new_edges)} เส้น"
    elif operation == "line":
        if directed:
            raise ValueError("Line Graph รองรับกราฟไม่มีทิศทาง")
        new_nodes = [
            {"id": index, "label": f"e{edge['id']}", "sourceEdge": edge["id"]}
            for index, edge in enumerate(edges, start=1)
        ]
        new_edges = []
        edge_id = 1
        for index, first in enumerate(edges):
            for other_index in range(index + 1, len(edges)):
                second = edges[other_index]
                if {first["u"], first["v"]} & {second["u"], second["v"]}:
                    new_edges.append({
                        "id": edge_id, "u": index + 1, "v": other_index + 1, "w": 1,
                    })
                    edge_id += 1
        return _result(
            "Line Graph", "graphTransform",
            [_step(f"สร้างจุดจากเส้นเดิม {len(edges)} เส้น; เชื่อมเมื่อเส้นเดิมมีจุดร่วม")],
            f'<div class="hero">Line Graph มี <b>{len(new_nodes)}</b> จุด และ <b>{len(new_edges)}</b> เส้น</div>',
            exists=True, directed=False, nodes=new_nodes, edges=new_edges,
        )
    elif operation == "induced":
        selected = payload.get("nodeIds")
        if not isinstance(selected, list) or any(
            isinstance(node_id, bool) or not isinstance(node_id, int) for node_id in selected
        ):
            raise ValueError("กรุณาระบุรายการรหัสจุดยอดสำหรับ Induced Subgraph")
        selected_set = set(selected)
        if not selected_set or not selected_set <= {node["id"] for node in nodes}:
            raise ValueError("Induced Subgraph ต้องเลือกจุดยอดที่มีอยู่ อย่างน้อย 1 จุด")
        new_nodes = [node for node in nodes if node["id"] in selected_set]
        new_edges = [edge for edge in edges if edge["u"] in selected_set and edge["v"] in selected_set]
        return _result(
            "Induced Subgraph", "graphTransform",
            [_step(f"เก็บ {len(new_nodes)} จุด และทุกเส้นที่ปลายทั้งสองอยู่ในชุดที่เลือก")],
            f'<div class="hero">Induced Subgraph มี <b>{len(new_nodes)}</b> จุด และ <b>{len(new_edges)}</b> เส้น</div>',
            exists=True, directed=directed, nodes=new_nodes, edges=new_edges,
        )
    else:
        raise ValueError("ไม่รู้จักการแปลงกราฟที่เลือก")

    result_nodes = [{"id": node["id"], "label": names[node["id"]]} for node in nodes]
    return _result(
        title, "graphTransform", [_step(message)],
        f'<div class="hero">{_html(message)}</div>',
        exists=True, directed=False, nodes=result_nodes, edges=new_edges,
    )


def _bipartite(payload: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, names, directed = _graph(payload)
    if directed:
        raise ValueError("Bipartite Graph ใช้กับกราฟไม่มีทิศทาง")

    ids = [node["id"] for node in nodes]
    adjacency = {node_id: set() for node_id in ids}
    for edge in edges:
        adjacency[edge["u"]].add(edge["v"])
        adjacency[edge["v"]].add(edge["u"])

    colors: dict[int, int] = {}
    conflict: tuple[int, int] | None = None
    for start in ids:
        if start in colors:
            continue
        colors[start] = 0
        queue = deque([start])
        while queue and conflict is None:
            node_id = queue.popleft()
            for neighbor in adjacency[node_id]:
                if neighbor not in colors:
                    colors[neighbor] = 1 - colors[node_id]
                    queue.append(neighbor)
                elif colors[neighbor] == colors[node_id]:
                    conflict = (node_id, neighbor)
                    break
        if conflict is not None:
            break

    if conflict is not None:
        first, second = (_name(names, node_id) for node_id in conflict)
        message = f"ไม่เป็น Bipartite: พบเส้น {first}–{second} เชื่อมจุดที่อยู่ฝั่งเดียวกัน"
        return _result(
            "Bipartite Graph", "bipartite",
            [_step("ตรวจพบเส้นที่ขัดกับการแบ่งจุดยอดเป็นสองฝั่ง")],
            f'<div class="hero warn">{_html(message)}</div>',
            exists=False, isBipartite=False, conflict=list(conflict),
        )

    left = [node_id for node_id in ids if colors[node_id] == 0]
    right = [node_id for node_id in ids if colors[node_id] == 1]
    left_names = ", ".join(_html(_name(names, node_id)) for node_id in left) or "—"
    right_names = ", ".join(_html(_name(names, node_id)) for node_id in right) or "—"
    message = f"เป็น Bipartite Graph: แบ่งได้ {len(left)} จุด และ {len(right)} จุด"
    return _result(
        "Bipartite Graph", "bipartite",
        [_step("ระบายสีแบบสองสีสำเร็จ: ทุกเส้นเชื่อมจุดคนละฝั่ง", fill=colors)],
        f'<div class="hero">{_html(message)}</div>'
        f'<div class="cards">{_card("ฝั่งที่ 1", left_names)}{_card("ฝั่งที่ 2", right_names)}</div>',
        exists=True, isBipartite=True, partitions=[left, right], colors=colors,
    )


def _isomorphism(payload: dict[str, Any]) -> dict[str, Any]:
    nodes_a, edges_a, names_a, directed_a = _graph(payload)
    other_graph = payload.get("otherGraph")
    if not isinstance(other_graph, dict):
        raise ValueError("กรุณาระบุกราฟอีกกราฟใน otherGraph")
    nodes_b, edges_b, names_b, directed_b = _graph(other_graph)
    if directed_a != directed_b:
        raise ValueError("กราฟทั้งสองต้องเป็นกราฟมีทิศทางชนิดเดียวกัน")
    if len(nodes_a) > 12 or len(nodes_b) > 12:
        raise ValueError("Isomorphism แบบ exact จำกัดไม่เกิน 12 จุดยอดต่อกราฟ")

    ids_a = [node["id"] for node in nodes_a]
    ids_b = [node["id"] for node in nodes_b]
    def adjacency_matrix(
        ids: list[int], edges: list[dict[str, Any]], label: str,
    ) -> list[list[bool]]:
        index = {node_id: position for position, node_id in enumerate(ids)}
        matrix = [[False] * len(ids) for _ in ids]
        for edge in edges:
            u, v = edge["u"], edge["v"]
            if u == v:
                raise ValueError(f"Isomorphism รองรับกราฟอย่างง่ายเท่านั้น: {label} มี Self-loop")
            i, j = index[u], index[v]
            if matrix[i][j] or (not directed_a and matrix[j][i]):
                raise ValueError(f"Isomorphism รองรับกราฟอย่างง่ายเท่านั้น: {label} มีเส้นขนาน")
            matrix[i][j] = True
            if not directed_a:
                matrix[j][i] = True
        return matrix

    matrix_a = adjacency_matrix(ids_a, edges_a, "กราฟแรก")
    matrix_b = adjacency_matrix(ids_b, edges_b, "กราฟที่สอง")
    if len(ids_a) != len(ids_b):
        return _result(
            "Isomorphic Graphs", "isomorphism",
            [_step("จำนวนจุดยอดไม่เท่ากัน จึงไม่มี Isomorphism")],
            '<div class="hero warn">ไม่ Isomorphic: จำนวนจุดยอดไม่เท่ากัน</div>',
            exists=False, isomorphic=False, mapping={},
        )
    if len(edges_a) != len(edges_b):
        return _result(
            "Isomorphic Graphs", "isomorphism",
            [_step("จำนวนเส้นเชื่อมไม่เท่ากัน จึงไม่มี Isomorphism")],
            '<div class="hero warn">ไม่ Isomorphic: จำนวนเส้นเชื่อมไม่เท่ากัน</div>',
            exists=False, isomorphic=False, mapping={},
        )
    count = len(ids_a)

    def initial_signatures(matrix: list[list[bool]]) -> list[tuple[int, ...]]:
        signatures = []
        for index in range(count):
            outgoing = sum(matrix[index])
            incoming = sum(matrix[row][index] for row in range(count))
            signatures.append((outgoing, incoming) if directed_a else (outgoing,))
        return signatures

    signatures_a = initial_signatures(matrix_a)
    signatures_b = initial_signatures(matrix_b)
    unique = sorted(set(signatures_a + signatures_b))
    signature_ids = {signature: index for index, signature in enumerate(unique)}
    colors_a = [signature_ids[signature] for signature in signatures_a]
    colors_b = [signature_ids[signature] for signature in signatures_b]

    def refine_colors() -> None:
        nonlocal colors_a, colors_b
        for _ in range(count):
            def signatures(matrix: list[list[bool]], colors: list[int]) -> list[tuple[Any, ...]]:
                refined = []
                for index in range(count):
                    outgoing = tuple(sorted(
                        colors[neighbor] for neighbor, connected in enumerate(matrix[index]) if connected
                    ))
                    incoming = tuple(sorted(
                        colors[neighbor] for neighbor in range(count) if matrix[neighbor][index]
                    ))
                    refined.append((
                        colors[index], outgoing,
                        incoming if directed_a else outgoing,
                    ))
                return refined

            next_a = signatures(matrix_a, colors_a)
            next_b = signatures(matrix_b, colors_b)
            palette = {
                signature: index
                for index, signature in enumerate(sorted(set(next_a + next_b)))
            }
            refined_a = [palette[signature] for signature in next_a]
            refined_b = [palette[signature] for signature in next_b]
            if refined_a == colors_a and refined_b == colors_b:
                break
            colors_a, colors_b = refined_a, refined_b

    refine_colors()
    color_counts_a = {color: colors_a.count(color) for color in set(colors_a)}
    color_counts_b = {color: colors_b.count(color) for color in set(colors_b)}
    if color_counts_a != color_counts_b:
        return _result(
            "Isomorphic Graphs", "isomorphism",
            [_step("การจัดกลุ่มจุดยอดตาม degree และเพื่อนบ้านไม่ตรงกัน")],
            '<div class="hero warn">ไม่ Isomorphic: โครงสร้าง degree/เพื่อนบ้านแตกต่างกัน</div>',
            exists=False, isomorphic=False, mapping={},
        )

    candidates = {
        index: [other for other, color in enumerate(colors_b) if color == colors_a[index]]
        for index in range(count)
    }
    mapping: dict[int, int] = {}
    used: set[int] = set()
    search_states = 0
    search_limit = 500_000
    exhausted = False

    def compatible(first: int, second: int) -> bool:
        if matrix_a[first][first] != matrix_b[second][second]:
            return False
        for mapped_first, mapped_second in mapping.items():
            if matrix_a[first][mapped_first] != matrix_b[second][mapped_second]:
                return False
            if matrix_a[mapped_first][first] != matrix_b[mapped_second][second]:
                return False
        return True

    def search() -> bool:
        nonlocal search_states, exhausted
        if len(mapping) == count:
            return True
        search_states += 1
        if search_states > search_limit:
            exhausted = True
            return False
        remaining = [
            index for index in range(count) if index not in mapping
        ]
        first = min(
            remaining,
            key=lambda index: (
                sum(candidate not in used for candidate in candidates[index]),
                -sum(matrix_a[index][other] for other in mapping),
                index,
            ),
        )
        for second in candidates[first]:
            if second in used or not compatible(first, second):
                continue
            mapping[first] = second
            used.add(second)
            if search():
                return True
            used.remove(second)
            del mapping[first]
            if exhausted:
                return False
        return False

    isomorphic = search()
    if exhausted:
        raise ValueError("ค้นหา Isomorphism เกินขีดจำกัด 500,000 สถานะ จึงยังสรุปผลไม่ได้")
    if not isomorphic:
        return _result(
            "Isomorphic Graphs", "isomorphism",
            [_step(f"ลองจับคู่จุดยอดครบ {search_states} สถานะแล้วไม่พบ mapping")],
            '<div class="hero warn">ไม่ Isomorphic: ไม่พบการจับคู่ที่รักษาเส้นเชื่อมทั้งหมด</div>',
            exists=False, isomorphic=False, mapping={}, searchStates=search_states,
        )

    result_mapping = {
        str(ids_a[first]): ids_b[second]
        for first, second in mapping.items()
    }
    rows = "".join(
        f"<tr><td>{_html(_name(names_a, ids_a[first]))}</td>"
        f"<td>{_html(_name(names_b, ids_b[second]))}</td></tr>"
        for first, second in sorted(mapping.items())
    )
    summary = (
        '<div class="hero">เป็น Isomorphic Graphs: พบการจับคู่ที่รักษาโครงสร้างเส้นเชื่อม</div>'
        '<div class="tw"><table class="tbl"><tr><th>กราฟแรก</th><th>กราฟที่สอง</th></tr>'
        f"{rows}</table></div>"
        '<div class="note">เปรียบเทียบโครงสร้างเท่านั้น โดยไม่สนชื่อจุดยอดหรือน้ำหนักเส้น</div>'
    )
    return _result(
        "Isomorphic Graphs", "isomorphism",
        [_step(f"พบ mapping ครบ {count} จุดยอด หลังค้นหา {search_states} สถานะ")],
        summary, exists=True, isomorphic=True, mapping=result_mapping,
        searchStates=search_states,
    )


def _euler(payload: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, names, directed = _graph(payload)
    ids = [node["id"] for node in nodes]
    if not ids:
        raise ValueError("ยังไม่มีจุดยอด")
    if len(edges) > 5000:
        raise ValueError("Euler Trail จำกัดที่ 5,000 เส้น เพื่อแสดงขั้นตอนได้เหมาะสม")

    degree = {node_id: 0 for node_id in ids}
    indegree = {node_id: 0 for node_id in ids}
    outdegree = {node_id: 0 for node_id in ids}
    weak: dict[int, set[int]] = {node_id: set() for node_id in ids}
    adjacency: dict[int, list[tuple[int, int]]] = {node_id: [] for node_id in ids}
    for edge in edges:
        u, v, edge_id = edge["u"], edge["v"], edge["id"]
        weak[u].add(v)
        weak[v].add(u)
        outdegree[u] += 1
        indegree[v] += 1
        if directed:
            adjacency[u].append((v, edge_id))
        elif u == v:
            degree[u] += 2
            adjacency[u].append((v, edge_id))
            adjacency[u].append((v, edge_id))
        else:
            degree[u] += 1
            degree[v] += 1
            adjacency[u].append((v, edge_id))
            adjacency[v].append((u, edge_id))

    active = {node_id for node_id in ids if outdegree[node_id] + indegree[node_id] > 0}
    if not directed:
        active = {node_id for node_id in ids if degree[node_id] > 0}
    connected = True
    if active:
        seen = {next(iter(active))}
        queue = list(seen)
        while queue:
            for target in weak[queue.pop()]:
                if target not in seen:
                    seen.add(target)
                    queue.append(target)
        connected = active <= seen

    if directed:
        starts = [node_id for node_id in ids if outdegree[node_id] - indegree[node_id] == 1]
        ends = [node_id for node_id in ids if indegree[node_id] - outdegree[node_id] == 1]
        balanced = all(abs(outdegree[node_id] - indegree[node_id]) <= 1 for node_id in ids)
        valid_degrees = balanced and (len(starts) == len(ends) == 1 or not starts and not ends)
        start = starts[0] if starts else next(iter(active), ids[0])
    else:
        odd = [node_id for node_id in ids if degree[node_id] % 2]
        valid_degrees = len(odd) in (0, 2)
        start = odd[0] if odd else next(iter(active), ids[0])
    possible = connected and valid_degrees
    if not possible:
        reasons = []
        if not connected:
            reasons.append("เส้นที่มี degree > 0 ไม่ได้อยู่ใน component เดียวกัน")
        if not valid_degrees:
            reasons.append("เงื่อนไข In/Out-degree ไม่ผ่าน" if directed else "จำนวนจุด degree คี่ต้องเป็น 0 หรือ 2")
        summary = f'<div class="hero warn">ไม่มี Euler Path/Circuit: {_html("; ".join(reasons))}</div>'
        if not directed:
            summary += f'<p>จุด degree คี่: {", ".join(_html(_name(names, node_id)) for node_id in odd) or "ไม่มี"}</p>'
        return _result("Euler Path / Circuit", "euler", [_step("ตรวจเงื่อนไข Euler แล้วไม่ผ่าน")], summary, exists=False)

    steps: list[dict[str, Any]] = [_step(
        f"เริ่ม Hierholzer ที่ {_name(names, start)}; ใช้ทุกเส้นหนึ่งครั้ง"
    )]
    used: set[int] = set()
    vertex_stack = [start]
    edge_stack: list[int] = []
    circuit_vertices: list[int] = []
    circuit_edges: list[int] = []
    while vertex_stack:
        current = vertex_stack[-1]
        while adjacency[current] and adjacency[current][-1][1] in used:
            adjacency[current].pop()
        if adjacency[current]:
            target, edge_id = adjacency[current].pop()
            used.add(edge_id)
            vertex_stack.append(target)
            edge_stack.append(edge_id)
            steps.append(_step(
                f"เดิน {_name(names, current)} → {_name(names, target)}",
                node={current: "visited", target: "current"},
                edge={edge_id: "consider"},
            ))
        else:
            circuit_vertices.append(vertex_stack.pop())
            if edge_stack:
                circuit_edges.append(edge_stack.pop())
    circuit_vertices.reverse()
    circuit_edges.reverse()
    if len(used) != len(edges):
        return _result(
            "Euler Path / Circuit", "euler", steps,
            '<div class="hero warn">กราฟไม่มี Euler Trail ที่ครอบคลุมทุกเส้น</div>', exists=False,
        )
    circuit_text = " → ".join(_html(_name(names, node_id)) for node_id in circuit_vertices)
    is_circuit = len(circuit_vertices) <= 1 or circuit_vertices[0] == circuit_vertices[-1]
    steps.append(_step(
        f"เสร็จสิ้น: {'Euler Circuit' if is_circuit else 'Euler Path'} — {circuit_text}",
        node={node_id: "path" for node_id in set(circuit_vertices)},
        edge={edge_id: "path" for edge_id in circuit_edges},
    ))
    summary = (
        f'<div class="hero">พบ {"Euler Circuit" if is_circuit else "Euler Path"} '
        f'({len(circuit_edges)} เส้น)</div><p>{circuit_text}</p>'
    )
    return _result(
        "Euler Path / Circuit (Hierholzer)", "euler", steps, summary,
        exists=True, isCircuit=is_circuit, order=circuit_vertices, edgeOrder=circuit_edges,
    )


def _edge_coloring(payload: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, names, directed = _graph(payload)
    ids = [node["id"] for node in nodes]
    if not ids:
        raise ValueError("ยังไม่มีจุดยอด")
    if len(edges) > 5000:
        raise ValueError("Edge Coloring จำกัดที่ 5,000 เส้น")

    incident: dict[int, set[int]] = {node_id: set() for node_id in ids}
    degree = {node_id: 0 for node_id in ids}
    for edge in edges:
        incident[edge["u"]].add(edge["id"])
        incident[edge["v"]].add(edge["id"])
        if edge["u"] == edge["v"]:
            degree[edge["u"]] += 2
        else:
            degree[edge["u"]] += 1
            degree[edge["v"]] += 1

    colors: dict[int, int] = {}
    ordered = sorted(
        edges,
        key=lambda edge: (
            -(degree[edge["u"]] + degree[edge["v"]]),
            edge["id"],
        ),
    )
    steps: list[dict[str, Any]] = [_step("เรียงเส้นตาม degree รอบจุดปลาย แล้วเลือกสีที่ไม่ชนเส้นประชิด")]
    for edge in ordered:
        conflicts = incident[edge["u"]] | incident[edge["v"]]
        unavailable = {colors[edge_id] for edge_id in conflicts if edge_id in colors}
        color = 0
        while color in unavailable:
            color += 1
        colors[edge["id"]] = color
        steps.append(_step(
            f"ระบาย { _name(names, edge['u']) }–{ _name(names, edge['v']) } ด้วยสี {color + 1}",
            edge={edge["id"]: "consider"},
        ))

    color_count = max(colors.values(), default=-1) + 1
    edge_by_id = {edge["id"]: edge for edge in edges}
    by_color = [
        [edge_id for edge_id, color in colors.items() if color == color_id]
        for color_id in range(color_count)
    ]
    summary = f'<div class="hero">ใช้สีเส้นทั้งหมด <b>{color_count}</b> สี</div>'
    for color_id, edge_ids in enumerate(by_color):
        edge_names = []
        for edge_id in edge_ids:
            edge = edge_by_id[edge_id]
            arrow = "→" if directed else "–"
            edge_names.append(f"{_html(_name(names, edge['u']))}{arrow}{_html(_name(names, edge['v']))}")
        summary += (
            f'<p><span class="sw" style="background:{_PALETTE[color_id % len(_PALETTE)]}"></span>'
            f' <b>สี {color_id + 1}:</b> {", ".join(edge_names) or "—"}</p>'
        )
    is_simple = all(edge["u"] != edge["v"] for edge in edges)
    if is_simple and not directed:
        maximum_degree = max(degree.values(), default=0)
        summary += (
            f'<div class="note">ทฤษฎีของ Vizing สำหรับกราฟ simple: '
            f'{maximum_degree} ≤ χ′(G) ≤ {maximum_degree + 1}. '
            "สีที่แสดงเป็นผล greedy จึงเป็นขอบเขตบน ไม่รับประกันค่าเหมาะที่สุด</div>"
        )
    return _result(
        "Edge Coloring (Greedy)", "edgeColor", steps, summary,
        colors=colors, colorCount=color_count, lowerBound=max(degree.values(), default=0),
    )


def _coloring(payload: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, names, directed = _graph(payload)
    if directed:
        raise ValueError("Coloring ใช้ได้เฉพาะกราฟไม่มีทิศทาง")
    if any(edge["u"] == edge["v"] for edge in edges):
        raise ValueError("ไม่สามารถระบายสีจุดยอดได้เมื่อมี Self-loop เพราะจุดต้องมีสีต่างจากตัวเอง")
    ids = [node["id"] for node in nodes]
    if not ids:
        raise ValueError("ยังไม่มีจุดยอด")
    neighbors: dict[int, set[int]] = {node_id: set() for node_id in ids}
    for edge in edges:
        if edge["u"] != edge["v"]:
            neighbors[edge["u"]].add(edge["v"])
            neighbors[edge["v"]].add(edge["u"])
    order = sorted(ids, key=lambda node_id: (-len(neighbors[node_id]), node_id))
    colors: dict[int, int] = {}
    color_names = payload.get("colorNames", [])
    def color_name(color: int) -> str:
        return color_names[color] if color < len(color_names) and color_names[color] else f"สี {color + 1}"

    def color_token(color: int) -> str:
        return f"{{{{COLOR_NAME_{color}}}}}"

    steps: list[dict[str, Any]] = []
    def snap(message: str, node: dict[int, str] | None = None, edge: dict[int, str] | None = None) -> None:
        steps.append(_step(message, fill=dict(colors), node=node or {}, edge=edge or {}))

    order_text = ", ".join(f"{_name(names, node_id)}({len(neighbors[node_id])})" for node_id in order)
    snap(f"Welsh–Powell: เรียงจุดตาม Degree มาก→น้อย: {order_text}")
    color = 0
    while len(colors) < len(order):
        snap(f'🎨 เริ่มใช้สีที่ {color + 1} "{color_name(color)}" — ไล่ตามลำดับ ใส่สีให้จุดที่ไม่ติดกับจุดสีนี้')
        for node_id in order:
            if node_id in colors:
                continue
            conflict = next((neighbor for neighbor in neighbors[node_id] if colors.get(neighbor) == color), None)
            if conflict is None:
                colors[node_id] = color
                snap(f'{_name(names, node_id)} ไม่ติดกับจุดที่ใช้ "{color_name(color)}" → ระบายสีนี้', {node_id: "current"})
            else:
                crossing = next((edge for edge in edges if (edge["u"] == node_id and edge["v"] == conflict) or (edge["v"] == node_id and edge["u"] == conflict)), None)
                snap(f'{_name(names, node_id)} ติดกับ {_name(names, conflict)} ที่ใช้ "{color_name(color)}" แล้ว → ข้ามไปก่อน', {node_id: "current"}, {crossing["id"]: "consider"} if crossing else {})
        color += 1
    color_count = color
    delta = max((len(neighbors[node_id]) for node_id in ids), default=0)

    exact: tuple[int, dict[int, int]] | None = None
    if len(ids) <= 15:
        exact_order = sorted(ids, key=lambda node_id: -len(neighbors[node_id]))
        exact_colors: dict[int, int] = {}
        def backtrack(index: int, limit: int, used: int) -> bool:
            if index == len(exact_order):
                return True
            node_id = exact_order[index]
            for candidate_color in range(min(limit, used + 1)):
                if all(exact_colors.get(neighbor) != candidate_color for neighbor in neighbors[node_id]):
                    exact_colors[node_id] = candidate_color
                    if backtrack(index + 1, limit, max(used, candidate_color + 1)):
                        return True
                    del exact_colors[node_id]
            return False
        for limit in range(1, len(ids) + 1):
            exact_colors.clear()
            if backtrack(0, limit, 0):
                exact = (limit, dict(exact_colors))
                break
    done_message = f"✔ เสร็จสิ้น! Greedy ใช้ {color_count} สี (ขอบเขตบน Δ+1 = {delta + 1})" + (f" | Chromatic Number χ(G) = {exact[0]}" if exact else "")
    snap(done_message)

    summary = f'<div class="hero">🎨 Welsh–Powell ใช้ <span class="bignum">{color_count}</span> สี' + (f' • ค่าที่ดีที่สุดจริง χ(G) = <b>{exact[0]}</b>' if exact else "") + "</div>"
    exact_value = str(exact[0]) if exact else "คำนวณเมื่อ |V| ≤ 15"
    summary += '<div class="cards">' + _card("Greedy (Welsh–Powell)", f"{color_count} สี") + _card("Δ (Degree สูงสุด)", delta) + _card("ขอบเขตบน Δ+1", delta + 1) + _card("χ(G) แบบ Exact", exact_value) + "</div>"
    if exact:
        summary += f"<p>⚠ Greedy ใช้สีมากกว่าค่าที่ดีที่สุด {color_count - exact[0]} สี (Greedy ไม่รับประกันว่าน้อยที่สุดเสมอ)</p>" if exact[0] < color_count else "<p>✔ Greedy ได้จำนวนสีเท่ากับค่าที่ดีที่สุด</p>"
    summary += '<h3>กลุ่มของแต่ละสี (กดตั้งชื่อความหมายได้)</h3>'
    for color in range(color_count):
        members = [node for node in nodes if colors[node["id"]] == color]
        chips = "".join(f'<span class="chip">{_html(node["label"])}</span>' for node in members)
        swatch = _PALETTE[color % len(_PALETTE)]
        summary += f'<div class="grp"><div class="gh"><span><span class="sw" style="background:{swatch}"></span>{color_token(color)} <small>({len(members)} จุด)</small></span><button type="button" class="btn mini" data-cname="{color}">✏️ ตั้งชื่อ</button></div>{chips}</div>'
    summary += '<h3>ลำดับ Welsh–Powell</h3><div class="tw"><table class="tbl"><tr><th>#</th><th>จุด</th><th>deg</th><th>สี</th></tr>'
    for index, node_id in enumerate(order, 1):
        summary += f'<tr><td>{index}</td><td class="l">{_html(_name(names, node_id))}</td><td>{len(neighbors[node_id])}</td><td class="l"><span class="sw" style="background:{_PALETTE[colors[node_id] % len(_PALETTE)]}"></span>{color_token(colors[node_id])}</td></tr>'
    summary += "</table></div><div class=\"note\">จุดที่เชื่อมกัน = ขัดแย้งกัน (เช่น วิชาที่มีนักเรียนสอบซ้อน หรือสินค้าที่ห้ามเก็บรวมกัน) จึงต้องได้สีต่างกัน แต่ละสีจึงหมายถึงช่วงเวลาสอบหรือช่องจัดเก็บ 1 ช่อง จำนวนสีจึงเท่ากับจำนวนช่วงเวลาหรือช่องที่ต้องใช้</div>"
    return _result("📊 สรุปผล Graph Coloring", "color", steps, summary, colors=colors)


def _flow(payload: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, names, directed = _graph(payload)
    if not directed:
        raise ValueError("Max Flow ใช้ได้เฉพาะกราฟมีทิศทาง")
    ids = [node["id"] for node in nodes]
    source, sink = payload.get("source"), payload.get("sink")
    if source not in names or sink not in names:
        raise ValueError("กรุณาเลือก Source และ Sink ก่อนรัน Max Flow")
    if source == sink:
        raise ValueError("Source และ Sink ต้องเป็นคนละจุด")
    if any(edge["w"] < 0 for edge in edges):
        raise ValueError("ความจุของเส้นเชื่อมต้องไม่ติดลบ")

    graph: dict[int, list[dict[str, Any]]] = {node_id: [] for node_id in ids}
    original_arcs: list[dict[str, Any]] = []
    def add_arc(u: int, v: int, capacity: float, edge_id: int, sign: int) -> None:
        forward: dict[str, Any] = {"to": v, "cap": capacity, "flow": 0, "eid": edge_id, "sign": sign}
        backward: dict[str, Any] = {"to": u, "cap": 0, "flow": 0, "eid": None, "sign": 0}
        forward["rev"] = backward
        backward["rev"] = forward
        graph[u].append(forward)
        graph[v].append(backward)
        original_arcs.append(forward)

    for edge in edges:
        if edge["u"] == edge["v"]:
            continue
        add_arc(edge["u"], edge["v"], edge["w"], edge["id"], 1)
        if not directed:
            add_arc(edge["v"], edge["u"], edge["w"], edge["id"], -1)

    def flow_of() -> dict[int, float]:
        flow = {edge["id"]: 0 for edge in edges}
        for arc in original_arcs:
            flow[arc["eid"]] += arc["sign"] * arc["flow"]
        return flow

    steps: list[dict[str, Any]] = []
    augmentations: list[tuple[list[int], float, bool]] = []
    total: float = 0

    def base() -> dict[str, Any]:
        flows = flow_of()
        edge_text: dict[int, str] = {}
        edge_state: dict[int, str] = {}
        for edge in edges:
            value = abs(flows[edge["id"]])
            edge_text[edge["id"]] = f"{_fmt(value)}/{_fmt(edge['w'])}"
            if value > 1e-9:
                edge_state[edge["id"]] = "sat" if value >= edge["w"] - 1e-9 else "flow"
        return {"etext": edge_text, "edge": edge_state}

    def snap(message: str, node: dict[int, str] | None = None, edge: dict[int, str] | None = None) -> None:
        current = base()
        if node:
            current["node"] = node
        if edge:
            current["edge"].update(edge)
        steps.append(_step(message, **current))

    snap(f"เริ่มต้น: Flow ทุกเส้น = 0 (แสดงเป็น flow/capacity) | Source = {_name(names, source)}, Sink = {_name(names, sink)}", {source: "current", sink: "current"})
    for iteration in range(1, 10001):
        parent: dict[int, tuple[int, dict[str, Any]] | None] = {source: None}
        queue = deque([source])
        while queue and sink not in parent:
            current = queue.popleft()
            for arc in graph[current]:
                if arc["cap"] - arc["flow"] > 1e-9 and arc["to"] not in parent:
                    parent[arc["to"]] = (current, arc)
                    queue.append(arc["to"])
        if sink not in parent:
            break
        path_arcs: list[dict[str, Any]] = []
        path_nodes = [sink]
        current = sink
        bottleneck = math.inf
        while current != source:
            parent_item = parent[current]
            assert parent_item is not None
            previous, arc = parent_item
            path_arcs.append(arc)
            bottleneck = min(bottleneck, arc["cap"] - arc["flow"])
            current = previous
            path_nodes.append(current)
        path_arcs.reverse()
        path_nodes.reverse()
        edge_state = {arc["eid"] if arc["eid"] is not None else arc["rev"]["eid"]: "consider" for arc in path_arcs}
        node_state = {node_id: "consider" for node_id in path_nodes}
        uses_reverse = any(arc["eid"] is None for arc in path_arcs)
        path_text = " → ".join(_name(names, node_id) for node_id in path_nodes)
        snap(f"รอบ {iteration}: BFS พบ Augmenting Path {path_text} | คอขวดของเส้นทาง = {_fmt(bottleneck)}" + (" (มีการดันกระแสย้อนกลับผ่าน residual edge)" if uses_reverse else ""), node_state, edge_state)
        for arc in path_arcs:
            arc["flow"] += bottleneck
            arc["rev"]["flow"] -= bottleneck
        total += bottleneck
        augmentations.append((path_nodes, bottleneck, uses_reverse))
        snap(f"เพิ่ม Flow +{_fmt(bottleneck)} ตามเส้นทางนี้ → Flow รวม = {_fmt(total)}", node_state, {edge_id: "path" for edge_id in edge_state})

    reachable = {source}
    queue = deque([source])
    while queue:
        current = queue.popleft()
        for arc in graph[current]:
            if arc["cap"] - arc["flow"] > 1e-9 and arc["to"] not in reachable:
                reachable.add(arc["to"])
                queue.append(arc["to"])
    cut = [edge for edge in edges if (edge["u"] in reachable and edge["v"] not in reachable) or (not directed and edge["v"] in reachable and edge["u"] not in reachable)]
    cut_capacity = sum(edge["w"] for edge in cut)
    snap(f"ไม่พบ Augmenting Path อีกแล้ว → Max Flow = {_fmt(total)}")
    cut_names = ", ".join(f'{_name(names, edge["u"])}–{_name(names, edge["v"])}' for edge in cut) or "-"
    reachable_names = ", ".join(_name(names, node_id) for node_id in reachable)
    snap(f"✔ Min Cut: ฝั่ง S = {{{reachable_names}}} | เส้นคอขวด: {cut_names} | ความจุรวม = {_fmt(cut_capacity)} = Max Flow", {node_id: "inS" for node_id in reachable}, {edge["id"]: "cut" for edge in cut})

    final_flows = flow_of()
    cut_ids = {edge["id"] for edge in cut}
    summary = f'<div class="hero">🚰 ปริมาณไหลสูงสุดจาก <b>{_html(_name(names, source))}</b> ไป <b>{_html(_name(names, sink))}</b> = <span class="bignum">{_fmt(total)}</span></div>'
    summary += '<div class="cards">' + _card("จำนวนรอบ Augment", len(augmentations)) + _card("ความจุ Min Cut", _fmt(cut_capacity)) + _card("เส้นคอขวด", f"{len(cut)} เส้น") + _card("Max Flow = Min Cut", "✔ จริง" if math.isclose(total, cut_capacity, abs_tol=1e-9) else "✘") + "</div>"
    summary += '<h3>🔴 เส้นคอขวด (Min Cut)</h3>' + ("".join(f'<span class="chip" style="background:#ffd6d6">{_html(_name(names, edge["u"]))}–{_html(_name(names, edge["v"]))} ({_fmt(edge["w"])})</span>' for edge in cut) if cut else "<p>-</p>")
    side_s = " ".join(f'<span class="chip">{_html(_name(names, node_id))}</span>' for node_id in reachable)
    side_t = " ".join(f'<span class="chip">{_html(names[node_id])}</span>' for node_id in ids if node_id not in reachable)
    summary += f'<p style="font-size:14px">ฝั่ง S: {side_s}<br>ฝั่ง T: {side_t}</p>'
    summary += '<h3>Augmenting Paths ทีละรอบ</h3><div class="tw"><table class="tbl"><tr><th>รอบ</th><th>เส้นทาง</th><th>เพิ่ม</th></tr>'
    for index, (path, amount, uses_reverse) in enumerate(augmentations, 1):
        path_text = " → ".join(_html(_name(names, node_id)) for node_id in path) + (" ↺" if uses_reverse else "")
        summary += f"<tr><td>{index}</td><td class=\"l\">{path_text}</td><td><b>+{_fmt(amount)}</b></td></tr>"
    summary += "</table></div><h3>Flow บนแต่ละเส้น</h3><div class=\"tw\"><table class=\"tbl\"><tr><th>เส้น</th><th>Flow / Capacity</th><th>สถานะ</th></tr>"
    for edge in edges:
        value = final_flows[edge["id"]]
        absolute = abs(value)
        direction = f" ({_name(names, edge['u'])}→{_name(names, edge['v'])})" if not directed and absolute > 1e-9 and value > 0 else (f" ({_name(names, edge['v'])}→{_name(names, edge['u'])})" if not directed and absolute > 1e-9 else "")
        status = "🔴 คอขวด (เต็ม)" if edge["id"] in cut_ids else ("🟣 เต็ม" if absolute >= edge["w"] - 1e-9 and edge["w"] > 0 else f"เหลือ {_fmt(edge['w'] - absolute)}")
        summary += f'<tr><td class="l">{_html(_name(names, edge["u"]))}–{_html(_name(names, edge["v"]))}{_html(direction)}</td><td><b>{_fmt(absolute)}/{_fmt(edge["w"])}</b></td><td class="l">{status}</td></tr>'
    summary += "</table></div><div class=\"note\">ใช้ประเมินปริมาณสินค้าหรือการจราจรสูงสุดที่โครงข่ายรองรับได้ เส้นคอขวด (Min Cut) คือจุดที่ควรขยายก่อน เพราะถ้าเพิ่มความจุเส้นเหล่านี้ Max Flow จึงจะเพิ่มขึ้นได้</div>"
    return _result("📊 สรุปผล Max Flow (Edmonds–Karp)", "flow", steps, summary)


def _planarity(payload: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, names, directed = _graph(payload)
    ids = [node["id"] for node in nodes]
    if directed:
        raise ValueError("Planarity และ Kuratowski ใช้กับกราฟไม่มีทิศทาง")
    if not ids:
        raise ValueError("ยังไม่มีจุดยอด")
    if len(ids) > 10:
        raise ValueError("การตรวจ K₅/K₃,₃ minors แบบ exact จำกัดที่ 10 จุดยอด")
    if len(edges) > 100:
        raise ValueError("Planarity จำกัดที่ 100 เส้น")

    simple_edges = {
        (min(edge["u"], edge["v"]), max(edge["u"], edge["v"]))
        for edge in edges
        if edge["u"] != edge["v"]
    }
    vertex_count = len(ids)
    edge_count = len(simple_edges)
    adjacency = {node_id: set() for node_id in ids}
    for u, v in simple_edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    triangle_free = not any(
        v in adjacency[u] and w in adjacency[u] and w in adjacency[v]
        for u, v, w in combinations(ids, 3)
    )
    steps = [_step(
        f"ตรวจกราฟอย่างง่าย: |V| = {vertex_count}, |E| = {edge_count}; "
        "self-loop และเส้นขนานไม่เปลี่ยนผล planarity"
    )]
    if vertex_count >= 3 and edge_count > 3 * vertex_count - 6:
        steps.append(_step("ขัดกับขอบเขต Euler |E| ≤ 3|V|−6"))
        summary = (
            f'<div class="hero bad">ไม่เป็นกราฟเชิงระนาบ: '
            f'|E| = {edge_count} &gt; 3|V|−6 = {3 * vertex_count - 6}</div>'
        )
        return _result("Planarity / Kuratowski", "planarity", steps, summary, planar=False)
    if triangle_free and vertex_count >= 3 and edge_count > 2 * vertex_count - 4:
        steps.append(_step("ขัดกับขอบเขต Euler สำหรับกราฟ planar ที่ไม่มีสามเหลี่ยม"))
        summary = (
            f'<div class="hero bad">ไม่เป็นกราฟเชิงระนาบ: ไม่มีสามเหลี่ยมและ '
            f'|E| = {edge_count} &gt; 2|V|−4 = {2 * vertex_count - 4}</div>'
        )
        return _result("Planarity / Kuratowski", "planarity", steps, summary, planar=False)

    def make_state(
        blocks: tuple[tuple[int, ...], ...],
    ) -> tuple[tuple[tuple[int, ...], ...], tuple[int, ...]]:
        ordered = tuple(sorted(tuple(sorted(block)) for block in blocks))
        masks = [0] * len(ordered)
        for i, left in enumerate(ordered):
            for j in range(i + 1, len(ordered)):
                if any(
                    (min(u, v), max(u, v)) in simple_edges
                    for u in left for v in ordered[j]
                ):
                    masks[i] |= 1 << j
                    masks[j] |= 1 << i
        return ordered, tuple(masks)

    def find_kuratowski(
        blocks: tuple[tuple[int, ...], ...], masks: tuple[int, ...],
    ) -> tuple[str, list[list[int]]] | None:
        for chosen in combinations(range(len(blocks)), 5):
            if all(masks[u] & (1 << v) for u, v in combinations(chosen, 2)):
                return "K₅", [list(blocks[index]) for index in chosen]
        for chosen in combinations(range(len(blocks)), 6):
            first, *remaining = chosen
            for extra_left in combinations(remaining, 2):
                left = (first, *extra_left)
                right = tuple(index for index in chosen if index not in left)
                if all(masks[u] & (1 << v) for u in left for v in right):
                    return "K₃,₃", [list(blocks[index]) for index in (*left, *right)]
        return None

    initial = make_state(tuple((node_id,) for node_id in ids))
    queue = deque([initial])
    visited = {initial}
    max_states = 30000
    witness: tuple[str, list[list[int]]] | None = None
    exhausted = True
    while queue:
        blocks, masks = queue.popleft()
        witness = find_kuratowski(blocks, masks)
        if witness:
            break
        count = len(blocks)
        if count <= 5:
            continue

        successors: list[tuple[tuple[int, ...], ...]] = []
        for index in range(count):
            if count > 5:
                successors.append(blocks[:index] + blocks[index + 1:])
            for neighbor in range(index + 1, count):
                if masks[index] & (1 << neighbor):
                    merged = tuple(sorted(blocks[index] + blocks[neighbor]))
                    successors.append(
                        blocks[:index]
                        + blocks[index + 1:neighbor]
                        + blocks[neighbor + 1:]
                        + (merged,)
                    )
        for successor in successors:
            state = make_state(successor)
            if state in visited:
                continue
            if len(visited) >= max_states:
                exhausted = False
                queue.clear()
                break
            visited.add(state)
            queue.append(state)

    theorem_note = (
        '<div class="note">Kuratowski: กราฟไม่เป็น planar ก็ต่อเมื่อมี subdivision ของ K₅ หรือ K₃,₃; '
        'Wagner ให้เงื่อนไขเทียบเท่าด้วย minors</div>'
    )
    if witness:
        obstruction, branch_sets = witness
        branch_text = " • ".join(
            "{" + ", ".join(_html(_name(names, node_id)) for node_id in branch_set) + "}"
            for branch_set in branch_sets
        )
        steps.append(_step(
            f"พบ {obstruction} minor จากการลบจุดยอดและหดเส้น จึงไม่เป็นกราฟเชิงระนาบ"
        ))
        summary = (
            f'<div class="hero bad">ไม่เป็นกราฟเชิงระนาบ: พบ <b>{obstruction}</b> minor'
            f'<br>Branch sets: {branch_text}</div>{theorem_note}'
        )
        return _result(
            "Planarity / Kuratowski", "planarity", steps, summary,
            planar=False, obstruction=obstruction, branchSets=branch_sets,
        )
    if exhausted:
        steps.append(_step(f"ตรวจครบ {len(visited)} สถานะของการลบจุดยอดและหดเส้น"))
        summary = (
            '<div class="hero">เป็นกราฟเชิงระนาบ: ไม่พบ K₅ หรือ K₃,₃ minor</div>'
            + theorem_note
        )
        return _result("Planarity / Kuratowski", "planarity", steps, summary, planar=True)

    steps.append(_step(f"ตรวจแล้ว {len(visited)} สถานะ แต่ถึงขีดจำกัดการค้นหา"))
    summary = (
        '<div class="hero warn">ยังสรุปผลไม่ได้: ถึงขีดจำกัดการค้นหาก่อนพบ minor</div>'
        '<div class="note">ผ่านเกณฑ์ Euler อย่างเดียวไม่เพียงพอที่จะยืนยันว่าเป็น planar</div>'
    )
    return _result("Planarity / Kuratowski", "planarity", steps, summary, planar=None)


def run_algorithm(payload: dict[str, Any]) -> dict[str, Any]:
    algorithm = payload.get("algorithm")
    runners = {
        "dijkstra": _dijkstra,
        "bfs": _traversal,
        "prim": _prim,
        "kruskal": _kruskal,
        "connectivity": _connectivity,
        "vertexconnectivity": _vertex_connectivity,
        "edgeconnectivity": _edge_connectivity,
        "matching": _maximum_bipartite_matching,
        "assignment": _hungarian_assignment,
        "tspexact": lambda graph: _tsp(graph, "exact"),
        "tspnearest": lambda graph: _tsp(graph, "nearest"),
        "tsp2opt": lambda graph: _tsp(graph, "2opt"),
        "pruferdecode": _prufer_decode,
        "havelhakimi": _havel_hakimi,
        "hamiltonian": _hamiltonian,
        "transform": _graph_transform,
        "bipartite": _bipartite,
        "isomorphism": _isomorphism,
        "euler": _euler,
        "edgecolor": _edge_coloring,
        "color": _coloring,
        "flow": _flow,
        "planarity": _planarity,
    }
    if algorithm not in runners:
        raise ValueError("ไม่รู้จักอัลกอริทึมที่เลือก")
    return runners[algorithm](payload)
