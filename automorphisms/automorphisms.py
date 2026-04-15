from dataclasses import dataclass, field
import concurrent.futures
from typing import Dict

from graphs.graph import Graph, Vertex
from colorref.colorref_v1_0_0 import is_balanced, is_bijection
from colorref.colorref_v1_2_1 import MIN_COLOR, solve_colorref_transform
from graphs.graph_io import load_graph
from orchestration.dataclasses import AutomorphismsAnalResult
from .permv2 import permutation
from .basicpermutationgroup import Orbit, Stabilizer, FindNonTrivialOrbit

@dataclass
class AutoAnal:
    """Automorphism Analysis results"""
    automorphism_count: int
    generators: list[permutation]

@dataclass
class _AutSearchContext:
    """context for the automorphism search"""
    g: Graph # original graph
    h: Graph # copy of original graph (for compat with cref)
    mapping: dict
    inv_mapping: dict
    do_membership_testing: bool = field(default=True)
    generators: list[permutation] = field(default_factory=list)
    def add_generator(self, f: permutation) -> None:
        self.generators.append(f)

def is_member(f: permutation, generators: list[permutation]) -> bool:
    alpha = FindNonTrivialOrbit(generators)
    if alpha is None:
        return f.istrivial()
    orbit, transversal = Orbit(generators, alpha, True)
    beta = f[alpha]
    if beta not in orbit:
        return False
    idx = orbit.index(beta)
    u_beta = transversal[idx]
    stabilizer_gens = Stabilizer(generators, alpha)
    return is_member(-u_beta * f, stabilizer_gens)

def compute_order(generators: list[permutation]) -> int:
    alpha = FindNonTrivialOrbit(generators)
    if alpha is None:
        return 1
    orbit = Orbit(generators, alpha)
    stabilizer_gens = Stabilizer(generators, alpha)
    return len(orbit) * compute_order(stabilizer_gens)


def _extract_permutation(coloring: dict[int, list[Vertex]], ctx: _AutSearchContext) -> permutation:
    n = len(ctx.g.vertices)
    perm_mapping = [0] * n

    for color, cls in coloring.items():
        cls_list = list(cls)
        if cls_list[0] in ctx.g.vertices:
            u = cls_list[0]
            v_h = cls_list[1]
        else:
            u = cls_list[1]
            v_h = cls_list[0]

        v = ctx.inv_mapping[v_h]
        perm_mapping[ctx.g.vertices.index(u)] = ctx.g.vertices.index(v)

    return permutation(n, mapping=perm_mapping)


# branching based on branching_v1_0_3.py
def _generate_automorphism(d_seq: list, i_seq: list, ctx: _AutSearchContext, is_trivial_branch: bool) -> bool:
    graph_list = [ctx.g, ctx.h]
    initial_coloring = {v: MIN_COLOR for v in ctx.g.vertices + ctx.h.vertices}
    for i, (vertices) in enumerate(zip(d_seq, i_seq)):
        x_vertex, y_vertex = vertices
        initial_coloring[x_vertex] = MIN_COLOR + i + 1
        initial_coloring[y_vertex] = MIN_COLOR + i + 1
    coloring = solve_colorref_transform(graph_list, initial_coloring)

    if not is_balanced(graph_list, coloring):
        return False

    if is_bijection(ctx.g, ctx.h, coloring):
        f = _extract_permutation(coloring, ctx)
        if not ctx.do_membership_testing or not is_member(f, ctx.generators):
            ctx.add_generator(f)
        return True

    # copied 1:1 from Stanislaw's basic branching
    min_color_class : None | int = None
    for color, color_class in coloring.items():
        if len(color_class) == 4:
            min_color_class = color
            break
        elif len(color_class) > 4 and (min_color_class is None or len(color_class) < len(coloring[min_color_class])):
            min_color_class = color

    if min_color_class is None:
        return False

    class_to_fix = set(coloring[min_color_class])

    y_set = class_to_fix.intersection(set(ctx.h.vertices))
    x = list(class_to_fix.difference(y_set))[0]

    if is_trivial_branch:
        y_trivial = ctx.mapping[x]
        _generate_automorphism(d_seq + [x], i_seq + [y_trivial], ctx, is_trivial_branch=True)
        for y in y_set:
            if y == y_trivial:
                continue
            _generate_automorphism(d_seq + [x], i_seq + [y], ctx, is_trivial_branch=False)
        return False
    else:
        for y in y_set:
            if _generate_automorphism(d_seq + [x], i_seq + [y], ctx, is_trivial_branch=False):
                return True
        return False

def analyze_automorphisms(g: Graph, do_membership_testing: bool = True) -> AutoAnal:
    h, mapping = g.copy_with_mapping()
    ctx = _AutSearchContext(
        g=g,
        h=h,
        mapping=mapping,
        inv_mapping={v: u for u, v in mapping.items()},
        do_membership_testing=do_membership_testing
    )

    _generate_automorphism([], [], ctx, is_trivial_branch=True)
    
    order = compute_order(ctx.generators)
    return AutoAnal(automorphism_count=order, generators=ctx.generators)

def count_automorphisms(path: str) -> AutomorphismsAnalResult:
    results: AutomorphismsAnalResult = AutomorphismsAnalResult()
    with open(path, 'r') as f:
        graph_list = load_graph(f, read_list=True)
    for i, graph in enumerate(graph_list):
        results.list_of_automorphism_counts.append(analyze_automorphisms(graph).automorphism_count)
    return results

def count_automorphisms_multicore(path: str) -> AutomorphismsAnalResult:
    results: AutomorphismsAnalResult = AutomorphismsAnalResult()
    with open(path, 'r') as f:
        graph_list = load_graph(f, read_list=True)
    future_to_graph_idx : Dict[concurrent.futures.Future, int] = {}
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for i, graph in enumerate(graph_list):
            future = executor.submit(analyze_automorphisms, graph)
            future_to_graph_idx[future] = i
        for future in concurrent.futures.as_completed(future_to_graph_idx):
            graph_idx = future_to_graph_idx[future]
            try:
                auto_anal = future.result()
                results.list_of_automorphism_counts.append(auto_anal.automorphism_count)
            except Exception as exc:
                print(f"Graph {graph_idx} generated an exception: {exc}")
    return results