import math
from collections import defaultdict


class Graph:
    """
    Gnerate a graph structure
    """

    stagger_constellations = True
    stagger_systems = False
    constellation_spacing_x = 18
    constellation_spacing_y = 10
    system_spacing_x = 6.0
    system_spacing_y = 3
    constellation_grid_cols = 6
    constellation_grid_rows = 4
    overall_grid_width = 100
    overall_grid_height = 80
    max_pass = 200
    weight_multiplier = 2.0
    constellation_order_override = {}

    def __init__(self) -> None:
        pass

    def count_crossings(self, order, edges):
        pos = {node: i for i, node in enumerate(order)}
        crossings = 0
        for i, (a1, b1) in enumerate(edges):
            for a2, b2 in edges[i + 1 :]:
                if (pos[a1] - pos[a2]) * (pos[b1] - pos[b2]) < 0:
                    crossings += 1
        return crossings

    def weighted_barycenter_order(self, nodes, weighted_edges, weight_multiplier=1.0):
        neighbor_map = defaultdict(list)
        for (a, b), w in weighted_edges.items():
            adjusted_weight = w * weight_multiplier
            neighbor_map[a].append((b, adjusted_weight))
            neighbor_map[b].append((a, adjusted_weight))
        barycenters = {}
        for node in nodes:
            neighbors = neighbor_map[node]
            if neighbors:
                total_weight = sum(w for n, w in neighbors if n in nodes)
                if total_weight > 0:
                    barycenters[node] = (
                        sum(nodes.index(n) * w for n, w in neighbors if n in nodes)
                        / total_weight
                    )
                else:
                    barycenters[node] = nodes.index(node)
            else:
                barycenters[node] = nodes.index(node)
        return sorted(nodes, key=lambda n: barycenters[n])

    def greedy_switch(self, order, edges):
        pass_num = 0
        improved = True
        while improved and pass_num < self.max_pass:
            improved = False
            for i in range(len(order) - 1):
                current_order = list(order)
                swapped_order = list(order)
                swapped_order[i], swapped_order[i + 1] = (
                    swapped_order[i + 1],
                    swapped_order[i],
                )
                if self.count_crossings(swapped_order, edges) < self.count_crossings(
                    current_order, edges
                ):
                    order = swapped_order
                    improved = True
            pass_num += 1
        return order

    def sifting(self, order, edges):
        pass_num = 0
        improved = True
        while improved and pass_num < self.max_pass:
            improved = False
            for i, node in enumerate(order):
                best_pos = i
                min_cross = self.count_crossings(order, edges)
                for j in range(len(order)):
                    if i == j:
                        continue
                    new_order = order[:]
                    new_order.pop(i)
                    new_order.insert(j, node)
                    cross = self.count_crossings(new_order, edges)
                    if cross < min_cross:
                        best_pos = j
                        min_cross = cross
                if best_pos != i:
                    node = order.pop(i)
                    order.insert(best_pos, node)
                    improved = True
            pass_num += 1
        return order

    def plot(self, geojson_data):
        points = [
            f for f in geojson_data["features"] if f["geometry"]["type"] == "Point"
        ]
        lines = [
            f for f in geojson_data["features"] if f["geometry"]["type"] == "LineString"
        ]

        # Group points by constellation
        constellation_dict = defaultdict(list)
        id_to_const = {}
        for pt in points:
            const_name = pt["properties"].get("constellation", "Unknown")
            constellation_dict[const_name].append(pt)
            id_to_const[pt["properties"]["id"]] = const_name

        # Count weighted edges between constellations
        weighted_inter_edges = defaultdict(int)
        intra_edges_by_const = defaultdict(list)
        for ln in lines:
            a, b = ln["properties"]["source"], ln["properties"]["target"]
            ca, cb = id_to_const[a], id_to_const[b]
            if ca == cb:
                intra_edges_by_const[ca].append((a, b))
            else:
                key = tuple(sorted((ca, cb)))
                weighted_inter_edges[key] += 1

        barycenter_edges = {}
        for (ca, cb), w in weighted_inter_edges.items():
            barycenter_edges[(ca, cb)] = w
            barycenter_edges[(cb, ca)] = w

        # Override constellation ordering
        constellations = list(constellation_dict.keys())
        if self.constellation_order_override is not None:
            const_order = [
                c for c in self.constellation_order_override if c in constellations
            ]
            # Append missing constellations at the end
            missing = [c for c in constellations if c not in const_order]
            const_order += missing
        else:
            const_order = self.weighted_barycenter_order(
                constellations,
                barycenter_edges,
                weight_multiplier=self.weight_multiplier,
            )
            inter_edges = []
            for (ca, cb), w in weighted_inter_edges.items():
                inter_edges.extend([(ca, cb)] * int(w * self.weight_multiplier))
            const_order = self.greedy_switch(const_order, inter_edges)
            const_order = self.sifting(const_order, inter_edges)

        # Grid positions
        num_const = len(const_order)
        if self.constellation_grid_cols is None:
            grid_cols = math.ceil(math.sqrt(num_const))
        else:
            grid_cols = self.constellation_grid_cols
        if self.constellation_grid_rows is None:
            grid_rows = math.ceil(num_const / grid_cols)
        else:
            grid_rows = self.constellation_grid_rows

        const_positions = {}
        for idx, const_name in enumerate(const_order):
            row = idx // grid_cols
            col = idx % grid_cols
            y_offset = (
                (self.constellation_spacing_y / 2)
                if (self.stagger_constellations and (col % 2 == 1))
                else 0
            )
            base_x = col * self.constellation_spacing_x
            # Invert y so graph reads top to bottom
            row = idx // grid_cols
            col = idx % grid_cols
            y_offset = (
                (self.constellation_spacing_y / 2)
                if (self.stagger_constellations and (col % 2 == 1))
                else 0
            )
            # Invert row for top-to-bottom rendering
            base_y = (grid_rows - 1 - row) * self.constellation_spacing_y + y_offset
            const_positions[const_name] = (base_x, base_y)

        # Scale
        if self.overall_grid_width or self.overall_grid_height:
            max_x = max(x for x, y in const_positions.values())
            max_y = max(y for x, y in const_positions.values())
            scale_x = (
                (self.overall_grid_width / max_x)
                if (self.overall_grid_width and max_x > 0)
                else 1.0
            )
            scale_y = (
                (self.overall_grid_height / max_y)
                if (self.overall_grid_height and max_y > 0)
                else 1.0
            )
            scale = min(scale_x, scale_y)
            for k in const_positions:
                x, y = const_positions[k]
                const_positions[k] = (x * scale, y * scale)
            self.system_spacing_x *= scale
            self.system_spacing_y *= scale

        # Override solar system ordering
        name_to_id = defaultdict(dict)
        for pt in points:
            const = pt["properties"].get("constellation", "Unknown")
            name = pt["properties"].get("name")
            sid = pt["properties"]["id"]
            name_to_id[const][name] = sid

        new_coords = {}
        for const_name in const_order:
            pts = constellation_dict[const_name]
            node_ids = [pt["properties"]["id"] for pt in pts]

            if (
                self.constellation_order_override is not None
                and const_name in self.constellation_order_override
            ):
                sys_order_raw = self.constellation_order_override[const_name]

                sys_order = []
                for s in sys_order_raw:
                    if s in node_ids:
                        sys_order.append(s)
                    elif s in name_to_id[const_name]:
                        sys_order.append(name_to_id[const_name][s])
                sys_missing = [sid for sid in node_ids if sid not in sys_order]
                node_order = sys_order + sys_missing
            else:
                intra_edges = intra_edges_by_const[const_name]
                node_order = self.weighted_barycenter_order(
                    node_ids, {(a, b): 1 for a, b in intra_edges}
                )
                node_order = self.greedy_switch(node_order, intra_edges)
                node_order = self.sifting(node_order, intra_edges)

            n = len(node_order)
            local_cols = math.ceil(math.sqrt(n))
            local_rows = math.ceil(n / local_cols)
            base_x, base_y = const_positions[const_name]

            for i, node_id in enumerate(node_order):
                lx = i % local_cols
                ly = i // local_cols
                # Invert ly for top-to-bottom rendering
                y_offset = (
                    (self.system_spacing_y / 2)
                    if (self.stagger_systems and (lx % 2 == 1))
                    else 0
                )
                new_x = base_x + lx * self.system_spacing_x
                new_y = (
                    base_y + (local_rows - 1 - ly) * self.system_spacing_y + y_offset
                )
                new_coords[node_id] = [new_x, new_y]

        # Unmilk the map with new coords
        for pt in points:
            pt["geometry"]["coordinates"] = new_coords[pt["properties"]["id"]]

        for ln in lines:
            start_id = ln["properties"]["source"]
            end_id = ln["properties"]["target"]
            ln["geometry"]["coordinates"] = [new_coords[start_id], new_coords[end_id]]

        return {"type": "FeatureCollection", "features": points + lines}
