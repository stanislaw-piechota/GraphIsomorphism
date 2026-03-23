from line_profiler_pycharm import profile
from typing import Iterable

from graphs.graph import Edge, Graph, Vertex
from graphs.graph_io import load_graph, write_visualization
import os

type TColorClass = dict[int, set[Vertex]]

@profile
def refine_step(color_classes: TColorClass, queue: list[int], max_color: int) -> tuple[list[int], int]:
  base_color = queue.pop(0)

  # TODO: computing A takes most time of refine step
  neighbouring_base: dict[Vertex, int] = dict()
  for base_vertex in color_classes[base_color]:
    for neighbour in base_vertex.neighbours:
      if neighbour in neighbouring_base:
        neighbouring_base[neighbour] += 1
      else:
        neighbouring_base[neighbour] = 1
  
  a: dict[int, set[Vertex]] = dict()
  for vertex, i in neighbouring_base.items():
    if i in a:
      a[i].add(vertex)
    else:
      a[i] = {vertex}

  for i, vertices in a.items():
    vertex_by_color: TColorClass = dict()
    for vertex in vertices:
      if vertex.color in vertex_by_color:
        vertex_by_color[vertex.color].add(vertex)
      else:
        vertex_by_color[vertex.color] = {vertex}

    for color_to_split, vertices in vertex_by_color.items():
      if len(vertices) != len(color_classes[color_to_split]):
        max_color += 1
        color_classes[max_color] = vertices
        color_classes[color_to_split] = color_classes[color_to_split] - vertices

        for v in vertices:
          v.color = max_color

        if color_to_split in queue:
          # color_to_split in queue
          queue.append(max_color)
        else:
          if len(vertices) < len(color_classes[color_to_split]):
            queue.append(max_color)
          else:
            queue.append(color_to_split)
  
  return queue, max_color

def compute_base_states(vertices: Iterable[Vertex]) -> tuple[TColorClass, int]:
  color_classes: TColorClass = dict()
  max_color: int = 0
  for vertex in vertices:
    if vertex.color in color_classes:
      color_classes[vertex.color].add(vertex)
    else:
      color_classes[vertex.color] = {vertex}
      max_color = max(max_color, vertex.color)
  return (color_classes, max_color)

@profile
def refine(vertices: Iterable[Vertex]) -> tuple[TColorClass, int]:

  color_classes, max_color = compute_base_states(vertices)
  # print(color_classes)
  # queue: list[int] = list(range(max_color+1))
  queue = [0]

  while len(queue) > 0:
    queue, max_color = refine_step(color_classes, queue, max_color)
  return color_classes, max_color

def initialize_colors(graphs: list[Graph], force: bool = False):
  for g in graphs:
    for v in g.vertices:
      if not hasattr(v, 'color') or force:
        v.color = 0

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

@profile
def count_isomorphisms(g: Graph, h: Graph, d_seq: list[Vertex], i_seq: list[Vertex]) -> int:
  graphs = [g, h]
  initialize_colors(graphs, force=True)

  for i, (x, y) in enumerate(zip(d_seq, i_seq)):
    x.color = i + 1
    y.color = i + 1

  color_classes, _ = refine([v for graph_vertices in [g.vertices for g in graphs] for v in graph_vertices])

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

@profile
def basic_branching(path: str):
  graphs: list[Graph]
  with open(path, 'r') as f:
    graphs = load_graph(f, Graph, True) # pyright: ignore[reportAssignmentType]

  isomorphic_graphs = [[0]]
  iso_counts = [0]

  for i, graph in enumerate(graphs[1:]):
    print(f"\nProcessing graph {i+1}")
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


def basic_colorref(path: str):
    with open(path, 'r') as f:
        graphs = load_graph(f, Graph, True)

    # graphs = [graphs[0]]
    initialize_colors(graphs)
    return refine([v for graph in graphs for v in graph.vertices])


if __name__ == '__main__':
    basic_colorref('input/colorref/colorref_largeexample_6_960.grl')
    # basic_colorref('input/fast_colorref/threepaths10240.gr')
    # basic_branching('input/branching/modulesD.grl')

    # create_report([
    #     # 'input/colorref',
    #     # 'input/fast_colorref/threepaths5.gr',
    #     # 'input/fast_colorref/threepaths10.gr',
    #     # 'input/fast_colorref/threepaths20.gr',
    #     # 'input/fast_colorref/threepaths40.gr',
    #     # 'input/fast_colorref/threepaths80.gr',
    #     # 'input/fast_colorref/threepaths160.gr',
    #     # 'input/fast_colorref/threepaths320.gr',
    #     # 'input/fast_colorref/threepaths640.gr',
    #     'input/fast_colorref',
    #     'input/branching'
    # ], {
    #     # 'fast colorref 1.1.0': old_colorref,
    #     'fast colorref 1.2.0': basic_colorref,
    # }, out_path='docs/colorref-1.2.0.tex', multiplier=1000)
