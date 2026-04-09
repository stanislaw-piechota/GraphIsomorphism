"""
Includes functions for reading and writing graphs, in a very simple readable format.
"""
# Version: 30-01-2015, Paul Bonsma
# Version: 29-01-2017, Pieter Bos
# Version: 13-06-2025, Wouter Fokkema

# updated 30-01-2015: writeDOT also writes color information for edges.
# updated 2-2-2015: writeDOT can also write directed graphs.
# updated 5-2-2015: no black fill color used, when more than numcolors**2 vertices.
# updated 29-1-2017: pep8 reformat, general improvements
# updated 13-06-2025: changed visualization functions, added graphML export, removed options, minor changes

import colorsys
from typing import IO, Tuple, List, Union
from graph import Graph, Vertex


# GraphML settings
COLORBLIND_MODE = False  # Start with variations in value and saturation rather than hue
TYPE_TO_STRING = {str: 'string', int: 'int', bool: 'bool', float: 'float'}
DEFAULT_ATTRIBUTES_GRAPHML = {'node': {'color': 'light gray', 'label': str, 'size': 30}, 'edge': {'color': 'black'}}

# Dot settings
NUM_COLORS = 12  # Make combinations of fillcolor and edgecolor in order to get more distinct nodes
USE_GRAPHML_COLORS = False  # Overwrite the .dot file color scheme by the graphML color scheme.
DEFAULT_ATTRIBUTES_DOT = {'node': {'penwidth': 1 if USE_GRAPHML_COLORS else 4, 'label': str, 'color': str, 'width': .5,
                                   'height': .5, 'margin': .05, 'style': 'filled', 'colorscheme': 'paired12'},
                          'edge': {'penwidth': 2}}


def num_to_color(n: int) -> str:
    """
    Converts natural numbers to colors such that numbers that are close together map to distinguishable colors.
    :param n: Natural number
    :return: Color in hex format as a string
    """
    n = int(n)
    sv_combs = [(0.8, 1), (0.2, 1), (0.8, 0.7)]

    if COLORBLIND_MODE:
        s, v = sv_combs[n % len(sv_combs)]
        hue_6 = (n//len(sv_combs)) % 6
    else:
        hue_6 = n % 6
        s, v = sv_combs[(n//6) % len(sv_combs)]

    n //= 6 * len(sv_combs)

    hue_rem = bin(n)[:1:-1]
    hue_frac = int(hue_rem, 2) / (1 << len(hue_rem))
    h = 1 - (hue_6 + hue_frac) / 6

    (r, g, b) = colorsys.hsv_to_rgb(h, s, v)
    (r, g, b) = (round(255*r), round(255*g), round(255*b))

    return f'#{r:02x}{g:02x}{b:02x}'


def read_line(f: IO[str]) -> str:
    """
    Read a single non-comment line from a file
    :param f: The file
    :return: The line
    """
    line = f.readline()

    while len(line) > 0 and line[0] == '#':
        line = f.readline()

    return line


def read_graph(graphclass, f: IO[str]) -> Tuple[Graph, bool]:
    """
    Read a graph from a file
    :param graphclass: The class of the graph
    :param f: The file
    :return: The graph
    """
    while True:
        try:
            line = read_line(f)
            n = int(line)
            graph = graphclass(n=n)
            break
        except ValueError:
            pass

    line = read_line(f)
    edges: list[tuple[int, int]] = []

    try:
        while True:
            comma = line.find(',')
            if ':' in line:
                colon = line.find(':')
                edges.append((int(line[:comma]), int(line[comma + 1:colon])))
            else:
                edges.append((int(line[:comma]), int(line[comma + 1:])))
            line = read_line(f)
    except:
        pass

    indexed_nodes: list[Vertex] = list(graph.vertices)

    for edge in edges:
        indexed_nodes[edge[0]].add_incidence(indexed_nodes[edge[1]])
        indexed_nodes[edge[1]].add_incidence(indexed_nodes[edge[0]])

    if line and line[0] == '-':
        return graph, True
    else:
        return graph, False


def read_graph_list(graph_class, f: IO[str]) -> List[Graph]:
    """
    Read a list of graphs from a file
    :param graph_class: The graph class
    :param f: The file
    :return: A list of graphs
    """
    graphs = []
    cont = True

    while cont:
        graph, cont = read_graph(graph_class, f)
        graphs.append(graph)

    return graphs


def load_graph(f: IO[str], graph_class=Graph, read_list: bool = False) -> Union[List[Graph], Graph]:
    """
    Load a graph from a file
    :param f: The file
    :param graph_class: Class of the graph. You may subclass the default graph class and add your own here.
    :param read_list: Specifies whether to read a list of graphs from the file, or just a single graph.
    :return: The graph, or a list of graphs.
    """
    if read_list:
        graph_list = read_graph_list(graph_class, f)
        return graph_list
    else:
        graph, _ = read_graph(graph_class, f)
        return graph



def write_line(f: IO[str], line: str):
    """
    Write a line to a file
    :param f: The file
    :param line: The line
    """
    f.write(line + '\n')


def get_attribute_value(attribute: str, obj, dict_or_default_or_type):
    """
    Helper function for the write_graphml and write_dot functions. Tries to determine whether obj has a given attribute.
    :param attribute:
    :param obj:
    :param dict_or_default_or_type:
    :return:
    """
    if isinstance(dict_or_default_or_type, dict):
        if obj in dict_or_default_or_type:
            return dict_or_default_or_type[obj]
        else:
            return None
    elif hasattr(obj, attribute):
        return getattr(obj, attribute)
    elif type(dict_or_default_or_type) is type:
        return None
    return dict_or_default_or_type


if __name__ == "__main__":
    with open('examplegraph.gr') as file:
        G = load_graph(file, Graph)
        print(G)
