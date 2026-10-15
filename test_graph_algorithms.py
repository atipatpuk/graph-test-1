import unittest

from graph_algorithms import run_algorithm


def graph_payload(algorithm: str, *, directed: bool, edges: list[dict], count: int = 4) -> dict:
    return {
        "algorithm": algorithm,
        "nodes": [{"id": node_id, "label": f"v{node_id}"} for node_id in range(1, count + 1)],
        "edges": edges,
        "directed": directed,
        "source": 1,
        "sink": count,
    }


class GraphAlgorithmTests(unittest.TestCase):
    def test_bfs_returns_expected_traversal_order(self):
        edges = [
            {"id": 1, "u": 1, "v": 2, "w": 1},
            {"id": 2, "u": 1, "v": 3, "w": 1},
            {"id": 3, "u": 2, "v": 4, "w": 1},
            {"id": 4, "u": 3, "v": 4, "w": 1},
        ]
        graph = graph_payload("bfs", directed=False, edges=edges)
        self.assertEqual(run_algorithm(graph)["order"], [1, 2, 3, 4])

    def test_bipartite_returns_two_partitions_and_vertex_colors(self):
        graph = graph_payload(
            "bipartite",
            directed=False,
            count=6,
            edges=[
                {"id": i + 1, "u": left, "v": right, "w": 1}
                for i, (left, right) in enumerate(
                    (left, right) for left in range(1, 4) for right in range(4, 7)
                )
            ],
        )
        result = run_algorithm(graph)
        self.assertTrue(result["isBipartite"])
        self.assertEqual(sorted(map(len, result["partitions"])), [3, 3])
        self.assertEqual(set(result["colors"]), set(range(1, 7)))

    def test_bipartite_rejects_odd_cycle_and_directed_graphs(self):
        triangle = graph_payload(
            "bipartite",
            directed=False,
            count=3,
            edges=[
                {"id": 1, "u": 1, "v": 2, "w": 1},
                {"id": 2, "u": 2, "v": 3, "w": 1},
                {"id": 3, "u": 3, "v": 1, "w": 1},
            ],
        )
        self.assertFalse(run_algorithm(triangle)["isBipartite"])
        triangle["directed"] = True
        with self.assertRaisesRegex(ValueError, "ไม่มีทิศทาง"):
            run_algorithm(triangle)

    def test_isomorphism_finds_mapping_between_relabelled_paths(self):
        first = graph_payload(
            "isomorphism",
            directed=False,
            count=4,
            edges=[
                {"id": 1, "u": 1, "v": 2, "w": 3},
                {"id": 2, "u": 2, "v": 3, "w": 4},
                {"id": 3, "u": 3, "v": 4, "w": 5},
            ],
        )
        first["otherGraph"] = {
            "nodes": [{"id": node_id, "label": f"other-{node_id}"} for node_id in range(1, 5)],
            "edges": [
                {"id": 1, "u": 1, "v": 3, "w": 100},
                {"id": 2, "u": 3, "v": 2, "w": 200},
                {"id": 3, "u": 2, "v": 4, "w": 300},
            ],
            "directed": False,
        }
        result = run_algorithm(first)
        self.assertTrue(result["isomorphic"])
        self.assertEqual(len(result["mapping"]), 4)

    def test_isomorphism_rejects_nonisomorphic_graphs_and_non_simple_input(self):
        first = graph_payload(
            "isomorphism",
            directed=False,
            count=4,
            edges=[
                {"id": 1, "u": 1, "v": 2, "w": 1},
                {"id": 2, "u": 2, "v": 3, "w": 1},
                {"id": 3, "u": 3, "v": 4, "w": 1},
            ],
        )
        first["otherGraph"] = {
            "nodes": [{"id": node_id} for node_id in range(1, 5)],
            "edges": [
                {"id": 1, "u": 1, "v": 2, "w": 1},
                {"id": 2, "u": 1, "v": 3, "w": 1},
                {"id": 3, "u": 1, "v": 4, "w": 1},
            ],
            "directed": False,
        }
        self.assertFalse(run_algorithm(first)["isomorphic"])
        first["otherGraph"]["edges"].append({"id": 4, "u": 1, "v": 2, "w": 1})
        with self.assertRaisesRegex(ValueError, "เส้นขนาน"):
            run_algorithm(first)

    def test_isomorphism_exact_search_distinguishes_cycle_from_two_triangles(self):
        graph = graph_payload(
            "isomorphism",
            directed=False,
            count=6,
            edges=[
                {"id": index + 1, "u": index + 1, "v": (index + 1) % 6 + 1, "w": 1}
                for index in range(6)
            ],
        )
        graph["otherGraph"] = {
            "nodes": [{"id": node_id, "label": f"b{node_id}"} for node_id in range(1, 7)],
            "edges": [
                {"id": 1, "u": 1, "v": 2, "w": 1},
                {"id": 2, "u": 2, "v": 3, "w": 1},
                {"id": 3, "u": 3, "v": 1, "w": 1},
                {"id": 4, "u": 4, "v": 5, "w": 1},
                {"id": 5, "u": 5, "v": 6, "w": 1},
                {"id": 6, "u": 6, "v": 4, "w": 1},
            ],
            "directed": False,
        }
        self.assertFalse(run_algorithm(graph)["isomorphic"])

    def test_koenigsberg_seven_bridges_have_no_euler_trail(self):
        graph = graph_payload(
            "euler",
            directed=False,
            count=4,
            edges=[
                {"id": 1, "u": 1, "v": 3, "w": 1},
                {"id": 2, "u": 1, "v": 3, "w": 1},
                {"id": 3, "u": 2, "v": 3, "w": 1},
                {"id": 4, "u": 2, "v": 3, "w": 1},
                {"id": 5, "u": 1, "v": 4, "w": 1},
                {"id": 6, "u": 2, "v": 4, "w": 1},
                {"id": 7, "u": 3, "v": 4, "w": 1},
            ],
        )
        self.assertFalse(run_algorithm(graph)["exists"])

    def test_removed_algorithms_are_not_registered(self):
        for algorithm in (
            "bellmanford", "dfs", "topological", "topologicaldfs", "scc",
            "floydwarshall", "dsatur", "tree",
        ):
            with self.subTest(algorithm=algorithm), self.assertRaises(ValueError):
                run_algorithm({"algorithm": algorithm})

    def test_kruskal_returns_minimum_spanning_tree_with_loops_and_parallel_edges(self):
        graph = graph_payload(
            "kruskal",
            directed=False,
            edges=[
                {"id": 1, "u": 1, "v": 1, "w": -10},
                {"id": 2, "u": 1, "v": 2, "w": 1},
                {"id": 3, "u": 1, "v": 2, "w": 7},
                {"id": 4, "u": 2, "v": 3, "w": 2},
                {"id": 5, "u": 3, "v": 4, "w": 3},
            ],
        )
        result = run_algorithm(graph)
        self.assertEqual(result["total"], 6)

    def test_euler_trail_uses_each_parallel_edge_and_loop_once(self):
        graph = graph_payload(
            "euler",
            directed=False,
            count=2,
            edges=[
                {"id": 1, "u": 1, "v": 1, "w": 1},
                {"id": 2, "u": 1, "v": 2, "w": 1},
                {"id": 3, "u": 1, "v": 2, "w": 1},
            ],
        )
        result = run_algorithm(graph)
        self.assertTrue(result["exists"])
        self.assertEqual(set(result["edgeOrder"]), {1, 2, 3})
        self.assertEqual(len(result["edgeOrder"]), 3)

    def test_euler_rejects_disconnected_active_components(self):
        graph = graph_payload(
            "euler",
            directed=False,
            edges=[
                {"id": 1, "u": 1, "v": 2, "w": 1},
                {"id": 2, "u": 3, "v": 4, "w": 1},
            ],
        )
        self.assertFalse(run_algorithm(graph)["exists"])

    def test_edge_coloring_assigns_different_colors_to_incident_edges(self):
        graph = graph_payload(
            "edgecolor",
            directed=False,
            edges=[
                {"id": 1, "u": 1, "v": 2, "w": 1},
                {"id": 2, "u": 1, "v": 3, "w": 1},
                {"id": 3, "u": 1, "v": 4, "w": 1},
                {"id": 4, "u": 2, "v": 3, "w": 1},
            ],
        )
        result = run_algorithm(graph)
        colors = result["colors"]
        for index, left in enumerate(graph["edges"]):
            for right in graph["edges"][index + 1:]:
                if {left["u"], left["v"]} & {right["u"], right["v"]}:
                    self.assertNotEqual(colors[left["id"]], colors[right["id"]])

    def test_vertex_coloring_reports_self_loop_as_impossible(self):
        graph = graph_payload(
            "color",
            directed=False,
            count=1,
            edges=[{"id": 1, "u": 1, "v": 1, "w": 1}],
        )
        with self.assertRaises(ValueError):
            run_algorithm(graph)

    def test_connectivity_finds_bridges_articulation_points_and_components(self):
        graph = graph_payload(
            "connectivity",
            directed=False,
            edges=[
                {"id": 1, "u": 1, "v": 2, "w": 1},
                {"id": 2, "u": 2, "v": 3, "w": 1},
                {"id": 3, "u": 3, "v": 1, "w": 1},
                {"id": 4, "u": 3, "v": 4, "w": 1},
            ],
        )
        result = run_algorithm(graph)
        self.assertEqual(result["bridges"], [4])
        self.assertEqual(result["articulationPoints"], [3])
        self.assertEqual(result["components"], 1)

    def test_connectivity_handles_parallel_edges_and_disconnected_vertices(self):
        graph = graph_payload(
            "connectivity",
            directed=False,
            count=3,
            edges=[
                {"id": 1, "u": 1, "v": 2, "w": 1},
                {"id": 2, "u": 1, "v": 2, "w": 1},
            ],
        )
        result = run_algorithm(graph)
        self.assertEqual(result["bridges"], [])
        self.assertEqual(result["articulationPoints"], [])
        self.assertEqual(result["components"], 2)

    def test_connectivity_rejects_directed_graphs(self):
        graph = graph_payload("connectivity", directed=True, edges=[])
        with self.assertRaises(ValueError):
            run_algorithm(graph)

    def test_vertex_and_edge_connectivity_for_cycles_and_complete_graphs(self):
        cycle = graph_payload(
            "vertexconnectivity",
            directed=False,
            count=4,
            edges=[
                {"id": 1, "u": 1, "v": 2, "w": 1},
                {"id": 2, "u": 2, "v": 3, "w": 1},
                {"id": 3, "u": 3, "v": 4, "w": 1},
                {"id": 4, "u": 4, "v": 1, "w": 1},
            ],
        )
        result = run_algorithm(cycle)
        self.assertEqual(result["kappa"], 2)
        self.assertEqual(len(result["cutVertices"]), result["kappa"])
        self.assertEqual(len(result["componentsAfterRemoval"]), 2)
        cycle["algorithm"] = "edgeconnectivity"
        edge_result = run_algorithm(cycle)
        self.assertEqual(edge_result["lambdaValue"], 2)
        self.assertEqual(len(edge_result["cutEdges"]), edge_result["lambdaValue"])
        self.assertEqual(len(edge_result["componentsAfterRemoval"]), 2)

        complete = graph_payload(
            "vertexconnectivity",
            directed=False,
            count=3,
            edges=[
                {"id": 1, "u": 1, "v": 2, "w": 1},
                {"id": 2, "u": 2, "v": 3, "w": 1},
                {"id": 3, "u": 1, "v": 3, "w": 1},
            ],
        )
        result = run_algorithm(complete)
        self.assertEqual(result["kappa"], 2)
        self.assertEqual(len(result["cutVertices"]), 2)
        complete["algorithm"] = "edgeconnectivity"
        result = run_algorithm(complete)
        self.assertEqual(result["lambdaValue"], 2)
        self.assertEqual(len(result["cutEdges"]), 2)

    def test_connectivity_returns_minimum_cuts_for_two_dense_parts_and_a_bridge(self):
        edges = [
            (1, 2), (1, 3), (2, 3),
            (4, 5), (4, 6), (5, 6),
            (3, 4),
        ]
        graph = graph_payload(
            "vertexconnectivity",
            directed=False,
            count=6,
            edges=[
                {"id": edge_id, "u": u, "v": v, "w": 1}
                for edge_id, (u, v) in enumerate(edges, 1)
            ],
        )
        result = run_algorithm(graph)
        self.assertEqual(result["kappa"], 1)
        self.assertEqual(len(result["cutVertices"]), 1)
        self.assertIn(result["cutVertices"][0], {3, 4})
        self.assertEqual(len(result["componentsAfterRemoval"]), 2)

        graph["algorithm"] = "edgeconnectivity"
        result = run_algorithm(graph)
        self.assertEqual(result["lambdaValue"], 1)
        self.assertEqual(result["cutEdges"], [7])
        self.assertEqual(len(result["componentsAfterRemoval"]), 2)

    def test_connectivity_values_ignore_edge_weights_and_handle_disconnected_graphs(self):
        path = graph_payload(
            "vertexconnectivity",
            directed=False,
            count=3,
            edges=[
                {"id": 1, "u": 1, "v": 2, "w": -10},
                {"id": 2, "u": 2, "v": 3, "w": 0},
            ],
        )
        result = run_algorithm(path)
        self.assertEqual(result["kappa"], 1)
        self.assertEqual(result["cutVertices"], [2])
        self.assertEqual(result["componentsAfterRemoval"], [[1], [3]])
        path["algorithm"] = "edgeconnectivity"
        result = run_algorithm(path)
        self.assertEqual(result["lambdaValue"], 1)
        self.assertEqual(result["cutEdges"], [1])
        self.assertEqual(len(result["componentsAfterRemoval"]), 2)

        path["nodes"].append({"id": 4, "label": "v4"})
        path["edges"] = [
            {"id": 1, "u": 1, "v": 2, "w": 1},
            {"id": 2, "u": 3, "v": 4, "w": 1},
        ]
        result = run_algorithm(path)
        self.assertEqual(result["lambdaValue"], 0)
        self.assertEqual(result["cutEdges"], [])
        self.assertEqual(len(result["componentsAfterRemoval"]), 2)
        path["algorithm"] = "vertexconnectivity"
        result = run_algorithm(path)
        self.assertEqual(result["kappa"], 0)
        self.assertEqual(result["cutVertices"], [])
        self.assertEqual(len(result["componentsAfterRemoval"]), 2)

    def test_edge_connectivity_counts_parallel_edges_separately(self):
        graph = graph_payload(
            "edgeconnectivity",
            directed=False,
            count=2,
            edges=[
                {"id": 1, "u": 1, "v": 2, "w": 9},
                {"id": 2, "u": 1, "v": 2, "w": -3},
                {"id": 3, "u": 1, "v": 2, "w": 0},
            ],
        )
        result = run_algorithm(graph)
        self.assertEqual(result["lambdaValue"], 3)
        self.assertEqual(result["cutEdges"], [1, 2, 3])
        self.assertEqual(len(result["componentsAfterRemoval"]), 2)

    def test_matching_finds_maximum_by_rerouting_an_existing_pair(self):
        graph = graph_payload(
            "matching",
            directed=False,
            count=4,
            edges=[
                {"id": 1, "u": 1, "v": 3, "w": 1},
                {"id": 2, "u": 1, "v": 4, "w": 1},
                {"id": 3, "u": 2, "v": 3, "w": 1},
            ],
        )
        result = run_algorithm(graph)
        self.assertEqual(result["size"], 2)
        self.assertEqual(
            {(pair["left"], pair["right"]) for pair in result["pairs"]},
            {(1, 4), (2, 3)},
        )
        self.assertEqual(len(result["matchedEdges"]), 2)
        cover = set(result["minimumVertexCover"])
        self.assertEqual(len(cover), result["size"])
        self.assertTrue(all(
            edge["u"] in cover or edge["v"] in cover
            for edge in graph["edges"]
        ))
        self.assertEqual(
            set(result["coverEdges"]),
            {edge["id"] for edge in graph["edges"]},
        )

    def test_matching_supports_disconnected_bipartite_graph_and_parallel_edges(self):
        graph = graph_payload(
            "matching",
            directed=False,
            count=5,
            edges=[
                {"id": 1, "u": 1, "v": 3, "w": 1},
                {"id": 2, "u": 1, "v": 3, "w": 2},
                {"id": 3, "u": 2, "v": 4, "w": 1},
            ],
        )
        result = run_algorithm(graph)
        self.assertEqual(result["size"], 2)
        self.assertEqual(len(result["minimumVertexCover"]), 2)

    def test_matching_rejects_non_bipartite_and_directed_graphs(self):
        graph = graph_payload(
            "matching",
            directed=False,
            count=3,
            edges=[
                {"id": 1, "u": 1, "v": 2, "w": 1},
                {"id": 2, "u": 2, "v": 3, "w": 1},
                {"id": 3, "u": 3, "v": 1, "w": 1},
            ],
        )
        with self.assertRaises(ValueError):
            run_algorithm(graph)
        graph["directed"] = True
        with self.assertRaises(ValueError):
            run_algorithm(graph)

    def test_hungarian_finds_minimum_cost_assignment(self):
        graph = graph_payload(
            "assignment",
            directed=False,
            count=4,
            edges=[
                {"id": 1, "u": 1, "v": 3, "w": 4},
                {"id": 2, "u": 1, "v": 4, "w": 1},
                {"id": 3, "u": 2, "v": 3, "w": 2},
                {"id": 4, "u": 2, "v": 4, "w": 5},
            ],
        )
        result = run_algorithm(graph)
        self.assertEqual(result["total"], 3)
        self.assertEqual(
            {(pair["left"], pair["right"], pair["edge"]) for pair in result["pairs"]},
            {(1, 4, 2), (2, 3, 3)},
        )
        self.assertEqual(result["size"], 2)
        self.assertEqual(set(result["matchedEdges"]), {2, 3})

    def test_hungarian_handles_rectangular_costs_and_parallel_edges(self):
        graph = graph_payload(
            "assignment",
            directed=False,
            count=3,
            edges=[
                {"id": 1, "u": 1, "v": 3, "w": 5},
                {"id": 2, "u": 2, "v": 3, "w": 4},
                {"id": 3, "u": 2, "v": 3, "w": 1},
            ],
        )
        result = run_algorithm(graph)
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["pairs"][0]["edge"], 3)

    def test_hungarian_transposes_unequal_sides_and_supports_negative_costs(self):
        graph = graph_payload(
            "assignment",
            directed=False,
            count=3,
            edges=[
                {"id": 1, "u": 1, "v": 3, "w": 2},
                {"id": 2, "u": 2, "v": 3, "w": -5},
            ],
        )
        result = run_algorithm(graph)
        self.assertEqual(result["total"], -5)
        self.assertEqual(result["pairs"], [{"left": 2, "right": 3, "cost": -5.0, "edge": 2}])

    def test_hungarian_rejects_impossible_or_invalid_assignments(self):
        impossible = graph_payload(
            "assignment",
            directed=False,
            count=4,
            edges=[
                {"id": 1, "u": 1, "v": 3, "w": 1},
                {"id": 2, "u": 1, "v": 4, "w": 2},
            ],
        )
        with self.assertRaisesRegex(ValueError, "ไม่มี Assignment"):
            run_algorithm(impossible)

        non_bipartite = graph_payload(
            "assignment",
            directed=False,
            count=3,
            edges=[
                {"id": 1, "u": 1, "v": 2, "w": 1},
                {"id": 2, "u": 2, "v": 3, "w": 1},
                {"id": 3, "u": 3, "v": 1, "w": 1},
            ],
        )
        with self.assertRaisesRegex(ValueError, "Bipartite"):
            run_algorithm(non_bipartite)
        non_bipartite["directed"] = True
        with self.assertRaises(ValueError):
            run_algorithm(non_bipartite)

    def test_prufer_decode_rejects_invalid_codes_and_handles_empty_code(self):
        result = run_algorithm({"algorithm": "pruferdecode", "code": []})
        self.assertEqual(len(result["nodes"]), 2)
        self.assertEqual(len(result["edges"]), 1)
        for invalid in (None, [0], [5, 1], [True]):
            with self.subTest(code=invalid):
                with self.assertRaises(ValueError):
                    run_algorithm({"algorithm": "pruferdecode", "code": invalid})

    def test_havel_hakimi_constructs_graph_for_graphical_sequence(self):
        result = run_algorithm({
            "algorithm": "havelhakimi",
            "degreeSequence": [3, 2, 2, 1],
        })
        self.assertTrue(result["exists"])
        degrees = [0] * len(result["nodes"])
        seen = set()
        for edge in result["edges"]:
            self.assertNotEqual(edge["u"], edge["v"])
            pair = (min(edge["u"], edge["v"]), max(edge["u"], edge["v"]))
            self.assertNotIn(pair, seen)
            seen.add(pair)
            degrees[edge["u"] - 1] += 1
            degrees[edge["v"] - 1] += 1
        self.assertEqual(sorted(degrees, reverse=True), [3, 2, 2, 1])

    def test_havel_hakimi_reports_non_graphical_sequences(self):
        result = run_algorithm({
            "algorithm": "havelhakimi",
            "degreeSequence": [3, 3, 1, 1],
        })
        self.assertFalse(result["exists"])
        self.assertFalse(result["graphical"])
        self.assertEqual(result["witness"], 2)
        odd = run_algorithm({
            "algorithm": "havelhakimi",
            "degreeSequence": [2, 1, 0],
        })
        self.assertFalse(odd["exists"])
        self.assertIsNone(odd["witness"])

    def test_hamiltonian_finds_cycle_and_reports_theorem_bounds(self):
        graph = graph_payload(
            "hamiltonian",
            directed=False,
            count=4,
            edges=[
                {"id": 1, "u": 1, "v": 2, "w": 1},
                {"id": 2, "u": 2, "v": 3, "w": 1},
                {"id": 3, "u": 3, "v": 4, "w": 1},
                {"id": 4, "u": 4, "v": 1, "w": 1},
            ],
        )
        result = run_algorithm(graph)
        self.assertTrue(result["exists"])
        self.assertTrue(result["cycle"])
        self.assertEqual(set(result["route"]), {1, 2, 3, 4})
        self.assertEqual(len(result["edgeOrder"]), 4)
        self.assertTrue(result["dirac"])
        self.assertTrue(result["ore"])

    def test_hamiltonian_falls_back_to_path_or_proves_none(self):
        path_graph = graph_payload(
            "hamiltonian",
            directed=False,
            count=4,
            edges=[
                {"id": 1, "u": 1, "v": 2, "w": 1},
                {"id": 2, "u": 2, "v": 3, "w": 1},
                {"id": 3, "u": 3, "v": 4, "w": 1},
            ],
        )
        path_result = run_algorithm(path_graph)
        self.assertTrue(path_result["exists"])
        self.assertFalse(path_result["cycle"])
        self.assertEqual(len(path_result["edgeOrder"]), 3)
        path_graph["edges"] = [{"id": 1, "u": 1, "v": 2, "w": 1}]
        no_path = run_algorithm(path_graph)
        self.assertFalse(no_path["exists"])
        self.assertTrue(no_path["complete"])

    def test_complement_and_line_graph_transform_edges_correctly(self):
        graph = graph_payload(
            "transform",
            directed=False,
            count=3,
            edges=[
                {"id": 1, "u": 1, "v": 2, "w": 5},
                {"id": 2, "u": 2, "v": 3, "w": 7},
            ],
        )
        graph["operation"] = "complement"
        complement = run_algorithm(graph)
        self.assertEqual(
            {(edge["u"], edge["v"]) for edge in complement["edges"]},
            {(1, 3)},
        )
        graph["operation"] = "line"
        line_graph = run_algorithm(graph)
        self.assertEqual(len(line_graph["nodes"]), 2)
        self.assertEqual(len(line_graph["edges"]), 1)

    def test_induced_subgraph_preserves_only_selected_nodes_and_internal_edges(self):
        graph = graph_payload(
            "transform",
            directed=True,
            edges=[
                {"id": 1, "u": 1, "v": 2, "w": 1},
                {"id": 2, "u": 2, "v": 3, "w": 1},
                {"id": 3, "u": 1, "v": 4, "w": 1},
            ],
        )
        graph["operation"] = "induced"
        graph["nodeIds"] = [1, 2, 3]
        result = run_algorithm(graph)
        self.assertTrue(result["directed"])
        self.assertEqual([node["id"] for node in result["nodes"]], [1, 2, 3])
        self.assertEqual([edge["id"] for edge in result["edges"]], [1, 2])

    def test_tsp_held_karp_finds_minimum_cycle(self):
        graph = graph_payload(
            "tspexact",
            directed=False,
            edges=[
                {"id": 1, "u": 1, "v": 2, "w": 10},
                {"id": 2, "u": 1, "v": 3, "w": 15},
                {"id": 3, "u": 1, "v": 4, "w": 20},
                {"id": 4, "u": 2, "v": 3, "w": 35},
                {"id": 5, "u": 2, "v": 4, "w": 25},
                {"id": 6, "u": 3, "v": 4, "w": 30},
            ],
        )
        result = run_algorithm(graph)
        self.assertTrue(result["exists"])
        self.assertTrue(result["optimal"])
        self.assertEqual(result["total"], 80)
        self.assertEqual(result["route"][0], 1)
        self.assertEqual(result["route"][-1], 1)
        self.assertEqual(set(result["route"][:-1]), {1, 2, 3, 4})

    def test_tsp_handles_directed_cycles_and_missing_tours(self):
        graph = graph_payload(
            "tspexact",
            directed=True,
            count=3,
            edges=[
                {"id": 1, "u": 1, "v": 2, "w": 2},
                {"id": 2, "u": 2, "v": 3, "w": 3},
                {"id": 3, "u": 3, "v": 1, "w": 4},
            ],
        )
        self.assertEqual(run_algorithm(graph)["total"], 9)
        graph["edges"].pop()
        self.assertFalse(run_algorithm(graph)["exists"])

    def test_tsp_nearest_neighbor_and_two_opt_return_closed_tours(self):
        graph = graph_payload(
            "tspnearest",
            directed=False,
            edges=[
                {"id": 1, "u": 1, "v": 2, "w": 10},
                {"id": 2, "u": 1, "v": 3, "w": 15},
                {"id": 3, "u": 1, "v": 4, "w": 20},
                {"id": 4, "u": 2, "v": 3, "w": 35},
                {"id": 5, "u": 2, "v": 4, "w": 25},
                {"id": 6, "u": 3, "v": 4, "w": 30},
            ],
        )
        nearest = run_algorithm(graph)
        self.assertTrue(nearest["exists"])
        graph["algorithm"] = "tsp2opt"
        improved = run_algorithm(graph)
        self.assertTrue(improved["exists"])
        self.assertLessEqual(improved["total"], nearest["total"])
        self.assertEqual(improved["route"][0], improved["route"][-1])


class PlanarityTests(unittest.TestCase):
    def test_planarity_accepts_cycle_graph(self):
        result = run_algorithm(graph_payload(
            "planarity",
            directed=False,
            count=4,
            edges=[
                {"id": 1, "u": 1, "v": 2, "w": 1},
                {"id": 2, "u": 2, "v": 3, "w": 1},
                {"id": 3, "u": 3, "v": 4, "w": 1},
                {"id": 4, "u": 4, "v": 1, "w": 1},
            ],
        ))
        self.assertIs(result["planar"], True)
        self.assertEqual(set(result["planarLayout"]), {"1", "2", "3", "4"})
        self.assertTrue(all(len(point) == 2 for point in result["planarLayout"].values()))

    def test_planarity_finds_kuratowski_k5(self):
        result = run_algorithm(graph_payload(
            "planarity",
            directed=False,
            count=5,
            edges=[
                {"id": edge_id, "u": u, "v": v, "w": 1}
                for edge_id, (u, v) in enumerate(combinations_for_test(5), 1)
            ],
        ))
        self.assertIs(result["planar"], False)

    def test_planarity_finds_kuratowski_k33(self):
        result = run_algorithm(graph_payload(
            "planarity",
            directed=False,
            count=6,
            edges=[
                {"id": edge_id, "u": u, "v": v, "w": 1}
                for edge_id, (u, v) in enumerate(
                    ((u, v) for u in (1, 2, 3) for v in (4, 5, 6)), 1
                )
            ],
        ))
        self.assertIs(result["planar"], False)

    def test_planarity_detects_k5_subdivision_by_contraction(self):
        edges = [
            (1, 2), (2, 3), (3, 4), (4, 5), (5, 1),
            (1, 3), (1, 4), (2, 4), (2, 5), (3, 5),
        ]
        edges.remove((1, 3))
        edges.extend(((1, 6), (6, 3)))
        result = run_algorithm(graph_payload(
            "planarity",
            directed=False,
            count=6,
            edges=[
                {"id": edge_id, "u": u, "v": v, "w": 1}
                for edge_id, (u, v) in enumerate(edges, 1)
            ],
        ))
        self.assertIs(result["planar"], False)
        self.assertEqual(result["obstruction"], "K₅")

    def test_planarity_detects_k33_subdivision_by_contraction(self):
        edges = [
            (1, 5), (1, 6), (2, 4), (2, 5), (2, 6),
            (3, 4), (3, 5), (3, 6), (1, 7), (7, 4),
        ]
        result = run_algorithm(graph_payload(
            "planarity",
            directed=False,
            count=7,
            edges=[
                {"id": edge_id, "u": u, "v": v, "w": 1}
                for edge_id, (u, v) in enumerate(edges, 1)
            ],
        ))
        self.assertIs(result["planar"], False)
        self.assertEqual(result["obstruction"], "K₃,₃")


def combinations_for_test(count: int) -> list[tuple[int, int]]:
    return [(u, v) for u in range(1, count + 1) for v in range(u + 1, count + 1)]


if __name__ == "__main__":
    unittest.main()
