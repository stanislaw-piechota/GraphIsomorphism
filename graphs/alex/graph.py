"""
This is a module for working with directed and undirected multigraphs.
"""
# version: 29-01-2015, Paul Bonsma
# version: 01-02-2017, Pieter Bos, Tariq Bontekoe
# version: 10-11-2025, Ruben Hoeksma

from typing import Iterator, Set


class GraphError(Exception):
    """
    An error that occurs while manipulating a `Graph`
    """

    def __init__(self, message: str):
        """
        Constructor
        :param message: The error message
        :type message: str
        """
        super(GraphError, self).__init__(message)


class Vertex(object):
    def __init__(self, graph: "Graph", label=None):
        if label is None:
            label = graph._next_label()

        self._graph = graph
        self.label = label
        self._incidence = set()
        self.color = 0
        self.i = -1

    def __repr__(self):
        return 'Vertex(label={}, #incident={})'.format(self.label, len(self._incidence))

    def __str__(self) -> str:
        return str(self.label)

    def is_adjacent(self, other: "Vertex") -> bool:
        return other in self._incidence

    def _add_incidence(self, vertex: "Vertex"):
        self._incidence.add(vertex)

    def __iadd__(self, vertex: "Vertex"):
        self._incidence.add(vertex)

    @property
    def graph(self) -> "Graph":
        return self._graph

    @property
    def neighbours(self) -> Set["Vertex"]:
        return self._incidence

    @property
    def degree(self) -> int:
        return len(self._incidence)
    
    def add_incidence(self, vertex: "Vertex"):
        self._add_incidence(vertex)


class Graph(object):
    def __init__(self, n: int=0):
        self._v: set[Vertex] = set()
        self._vdict: dict[int, Vertex] = {}
        self._next_label_value: int = 0

        for _ in range(n):
            self.add_vertex(Vertex(self))

    def _next_label(self) -> int:
        result = self._next_label_value
        self._next_label_value += 1
        return result

    @property
    def vertices(self) -> Set["Vertex"]:
        return self._v

    def add_vertex(self, vertex: "Vertex"):
        if vertex.graph != self:
            raise GraphError("A vertex must belong to the graph it is added to")

        self._v.add(vertex)
        self._vdict[vertex.label] = vertex

    def __iadd__(self, other: Vertex) -> "Graph":
        self.add_vertex(other)

        return self
    
    def __getitem__(self, key: int) -> "Vertex":
        return self._vdict[key]
    
    def __iter__(self) -> Iterator["Vertex"]:
        return iter(self._vdict.values())

    def is_adjacent(self, u: "Vertex", v: "Vertex") -> bool:
        return v in u.neighbours
    
    def copy(self) -> "Graph":
        result = Graph(len(self._v))

        for i, v in enumerate(result):
            orig = self[i]
            v.color = orig.color
            for neighbour in orig.neighbours:
                v.add_incidence(result[neighbour.label])

        return result

    def copy_with_mapping(self) -> tuple["Graph", dict[Vertex, Vertex]]:
        """Returns a copy of the graph alongside a mapping from original to new vertices."""
        result = self.copy()
        mapping = {orig: result[orig.label] for orig in self}
        return result, mapping

    def index(self, vertex: Vertex) -> int:
        """Returns the 0-based integer index of a given vertex."""
        return list(self._vdict.values()).index(vertex)