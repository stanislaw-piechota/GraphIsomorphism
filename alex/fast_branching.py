from line_profiler_pycharm import profile
from typing import Iterable
from graphs.graph import Edge, Graph, Vertex
from graphs.graph_io import load_graph, write_visualization
import os

type TColorClass = dict[int, set[Vertex]]

# neighbours_in = {
#   [color]: {
#     [i]: {
#       [v_color]: [vertices]
#     }
#   }
# }
# Each vertex in vertices is
#  - Of color `v_color`
#  - Has `i` neighbours of color `color`
type TColorClassToRefine = dict[int, dict[int, TColorClass]]

def refine_step(color_classes: TColorClass, neighbours_in: TColorClassToRefine, max_color: int, base_color: int):
  for i in neighbours_in[base_color]:
    for color, vertices in neighbours_in[base_color][i].items():
      if len(vertices) != len(color_classes[color]):
        max_color += 1
        color_classes[max_color] = vertices
        color_classes[color] = color_classes[color] - vertices

        for v in vertices:
          v.color = max_color
  
  return max_color

def refine(color_classes: TColorClass, neighbours_in: TColorClassToRefine, max_color: int) -> tuple[int, TColorClass]:
  keys = list(neighbours_in.keys())
  i = 0
  new_max_color = max_color

  while (new_max_color == max_color and i < len(keys)):
    new_max_color = refine_step(color_classes, neighbours_in, max_color, keys[i])
    i += 1
  return (new_max_color, color_classes)

def compute_base_states(vertices: Iterable[Vertex]) -> tuple[TColorClass, TColorClassToRefine, int]:
  color_classes: TColorClass = dict()
  neighbours_in: TColorClassToRefine = dict()
  max_color: int = 0

  for vertex in vertices:
    if vertex.color in color_classes:
      color_classes[vertex.color].add(vertex)
    else:
      color_classes[vertex.color] = set([vertex])

    neighbour_colors = [v.color for v in vertex.neighbours]
    for neighbour_color, neighbour_count in [(x, neighbour_colors.count(x)) for x in set(neighbour_colors)]:
      if neighbour_color not in neighbours_in:
        neighbours_in[neighbour_color] = dict()
      if neighbour_count not in neighbours_in[neighbour_color]:
        neighbours_in[neighbour_color][neighbour_count] = dict()
      if vertex.color in neighbours_in[neighbour_color][neighbour_count]:
        neighbours_in[neighbour_color][neighbour_count][vertex.color].add(vertex)
      else:
        neighbours_in[neighbour_color][neighbour_count][vertex.color] = set([vertex])
    
    max_color = max(max_color, vertex.color)
  
  return (color_classes, neighbours_in, max_color)

def refine_vertices(vertices: Iterable[Vertex]) -> tuple[int, TColorClass]:
  color_classes, neighbours_in, max_color = compute_base_states(vertices)
  new_max_color, color_classes = refine(color_classes, neighbours_in, max_color)

  while(new_max_color != max_color):
    color_classes, neighbours_in, max_color = compute_base_states(vertices)
    new_max_color, color_classes = refine(color_classes, neighbours_in, max_color)
  
  return (new_max_color, color_classes)

def initialize_colors(graphs: list[Graph], force: bool = False):
  for g in graphs:
    for v in g.vertices:
      if not hasattr(v, 'color') or force:
        v.color = 0

def combine_graphs(graphs: Iterable[Graph]) -> Graph:
  graphs_combined = Graph(False)
  for graph in graphs:
    vertex_map: dict[Vertex, Vertex] = {}

    for vertex in graph.vertices:
      new_vertex = Vertex(graphs_combined)
      if hasattr(vertex, 'color'):
        new_vertex.color = vertex.color
      vertex_map[vertex] = new_vertex
      graphs_combined += new_vertex

    for edge in graph.edges:
      orig_head = edge.head
      orig_tail = edge.tail

      head = vertex_map[orig_head]
      tail = vertex_map[orig_tail]

      new_edge = Edge(tail, head)
      graphs_combined += new_edge
  return graphs_combined

def save_graphs(graphs: Iterable[Graph], id: str = ''):
  graphs_combined = combine_graphs(graphs)
  with open(id + '.graphML', 'w+') as f:
    write_visualization(graphs_combined, f)

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

def count_isomorphisms(g: Graph, h: Graph, d_seq: list[Vertex], i_seq: list[Vertex]) -> int:
  graphs = [g, h]
  initialize_colors(graphs, force=True)

  for i, (x, y) in enumerate(zip(d_seq, i_seq)):
    x.color = i + 1
    y.color = i + 1

  _, color_classes = refine_vertices([v for graph_vertices in [g.vertices for g in graphs] for v in graph_vertices])

  if not is_balanced(g, h, color_classes):
    return 0

  if is_bijection(g, h, color_classes):
    return 1

  min_color_class : None | int = None
  for color, color_class in color_classes.items():
    if len(color_class) == 4:
      min_color_class = color
      break
    elif len(color_class) > 4 and (min_color_class is None or len(color_class) < len(color_classes[min_color_class])):
      min_color_class = color

  if min_color_class is None:
    return 0

  class_to_fix = set(color_classes[min_color_class])

  num = 0
  y_set = class_to_fix.intersection(set(h.vertices))
  x = list(class_to_fix.difference(y_set))[0]
  for y in y_set:
    num += count_isomorphisms(g, h, d_seq + [x], i_seq + [y])
  return num

def basic_branching(path: str):
  graphs: list[Graph]
  with open(path, 'r') as f:
    graphs = load_graph(f, Graph, True) # pyright: ignore[reportAssignmentType]

  isomorphic_graphs = [[0]]
  iso_counts = [0]

  for i, graph in enumerate(graphs[1:]):
    print(f"\nProcessing graph {i+2}")
    class_found = False
    for iso_idx, iso_class in enumerate(isomorphic_graphs[::]):
      print(f"Comparing with iso class {iso_idx+1}")
      base_graph = graphs[iso_class[0]]
      count = count_isomorphisms(base_graph, graph, [], [])
      if count != 0:
        iso_class.append(i+1)
        iso_counts[iso_idx] = count
        class_found = True
        break

    if not class_found:
      isomorphic_graphs.append([i+1])
      iso_counts.append(0)


  for i, iso_class in enumerate(isomorphic_graphs):
    print(iso_class, iso_counts[i])

def group_by_color(graphs: Iterable[Graph], color_classes: TColorClass) -> list[set[Graph]]:
  groups: list[set[Graph]] = []
  for graph in graphs:
    found = False
    for group in groups:
      if is_balanced(graph, next(iter(group)), color_classes):
        group.add(graph)
        found = True
        break
    if not found:
      groups.append(set([graph]))
  return groups

def run_colorref():
  path = "input/cref9vert3comp_10_27.grl"

  graphs: list[Graph]
  with open(path, "r") as f:
    graphs = load_graph(f, Graph, True)  # pyright: ignore[reportAssignmentType]

  initialize_colors(graphs)

  _, color_classes = refine_vertices([v for graph_vertices in [g.vertices for g in graphs] for v in graph_vertices])

  for group in group_by_color(graphs, color_classes):
    print(sorted([graphs.index(g) for g in group]))
  save_graphs(graphs, 'test/colorref')

def run_all_branching():
  for path in os.listdir("input/branching"):
    print(path)
    basic_branching('input/branching/' + path)
    print('-'*20)

@profile
def run_branching():
  path = "input/branching/wheeljoin14.grl"
  basic_branching(path)

if __name__ == '__main__':
  run_branching()
