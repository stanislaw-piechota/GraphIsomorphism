from collections import defaultdict

from graphs.graph import Graph, Vertex
from graphs.graph_io import load_graph

MIN_COLOR = 0

type TColorClass = dict[int, set[Vertex]]


# based on the color refinement in branching_v1_0_4 but adapted to work without the graphs copying
# uses dictionaries to store vertex colors to retain compat with normal graph class
def refine_step(color_classes: TColorClass, vertex_colors: dict[Vertex, int], queue: list[int], max_color: int) -> tuple[list[int], TColorClass, dict[Vertex, int], int]:
    base_color = queue.pop(0)

    visited: set[Vertex] = set()
    a: dict[int, set[Vertex]] = dict()
    vertex_i: dict[Vertex, int] = dict()

    for base_vertex in color_classes[base_color]:
        for v in base_vertex.neighbours:
            new_i = 0

            if v in visited:
                a[vertex_i[v]].remove(v)
                new_i = vertex_i[v] + 1
            #else:
            #    visited.add(v)

            vertex_i[v] = new_i
            if new_i in a:
                a[new_i].add(v)
            else:
                a[new_i] = set([v])

    for i, vertices in a.items():
        vertex_by_color: TColorClass = dict()
        for vertex in vertices:
            color = vertex_colors[vertex]
            if color in vertex_by_color:
                vertex_by_color[color].add(vertex)
            else:
                vertex_by_color[color] = set([vertex])

        for color_to_split, vertices in vertex_by_color.items():
            if len(vertices) != len(color_classes[color_to_split]):
                max_color += 1
                color_classes[max_color] = vertices
                color_classes[color_to_split] = color_classes[color_to_split] - vertices

                for v in vertices:
                    vertex_colors[v] = max_color

                if color_to_split in queue:
                    # color_to_split in queue
                    queue.append(max_color)
                else:
                    if len(vertices) < len(color_classes[color_to_split]):
                        queue.append(max_color)
                    else:
                        queue.append(color_to_split)

    return queue, color_classes, vertex_colors, max_color


def fast_solve_colorref_transform(initial_coloring: dict[Vertex, int]) -> TColorClass:
    color_classes: TColorClass = defaultdict(set)
    vertex_colors: dict[Vertex, int] = {}

    # initialize state
    for v, c in initial_coloring.items():
        color_classes[c].add(v)
        vertex_colors[v] = c

    max_color = max(color_classes.keys()) if color_classes else 0
    queue = list(color_classes.keys())

    while len(queue) > 0:
        queue, color_classes, vertex_colors, max_color = refine_step(color_classes, vertex_colors, queue, max_color)
    return dict(color_classes)

def is_balanced(g: Graph, h: Graph, color_classes: TColorClass) -> bool:
  g_vertices_set, h_vertices_set = set(g.vertices), set(h.vertices)
  for color_class in color_classes.values():
    if len(color_class.intersection(g_vertices_set)) != len(color_class.intersection(h_vertices_set)):
      return False
  return True

def is_bijection(g: Graph, h: Graph, color_classes: TColorClass) -> bool:
  g_vertices_set, h_vertices_set = set(g.vertices), set(h.vertices)
  for color_class in color_classes.values():
    if len(color_class.intersection(g_vertices_set)) != len(color_class.intersection(h_vertices_set)) or len(color_class.intersection(g_vertices_set)) > 1:
      return False
  return True


def fast_colorref(path: str):
    with open(path, 'r') as file:
        graph_list = load_graph(file, read_list=True)
    vertices = [vertex for graph in graph_list for vertex in graph.vertices]
    initial_coloring = {vertex: MIN_COLOR for vertex in vertices}
    coloring = fast_solve_colorref_transform(initial_coloring)
    return coloring