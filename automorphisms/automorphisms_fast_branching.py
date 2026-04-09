from dataclasses import dataclass, field

from graphs.alex.graph import Graph, Vertex
from branching.branching_v1_0_4 import refine, is_balanced, is_bijection

from .permv2 import permutation

from .automorphisms import AutoAnal, _AutSearchContext, is_member, compute_order

# extract_permutation adapted to work with graphs/alex/graph.py
def _extract_permutation(color_classes: dict[int, set[Vertex]], g_curr: Graph, h_curr: Graph, ctx: _AutSearchContext) -> permutation:
    n = len(ctx.g.vertices)
    perm_mapping = [0] * n

    for color, cls in color_classes.items():
        cls_list = list(cls)
        if cls_list[0] in g_curr.vertices:
            u_curr = cls_list[0]
            v_curr = cls_list[1]
        else:
            u_curr = cls_list[1]
            v_curr = cls_list[0]

        u_orig = ctx.g[u_curr.label]
        v_orig_in_h = ctx.h[v_curr.label]
        v_orig = ctx.inv_mapping[v_orig_in_h]

        perm_mapping[ctx.g.index(u_orig)] = ctx.g.index(v_orig)

    return permutation(n, mapping=perm_mapping)


# branching based on branching_v1_0_4.py (fast_branching_v3.py)
def _generate_automorphism(g_curr: Graph, h_curr: Graph, ctx: _AutSearchContext, is_trivial_branch: bool) -> bool:
    graphs = [g_curr, h_curr]
    color_classes, max_color = refine([v for graph_vertices in [g.vertices for g in graphs] for v in graph_vertices])

    if not is_balanced(g_curr, h_curr, color_classes):
        return False

    if is_bijection(g_curr, h_curr, color_classes):
        f = _extract_permutation(color_classes, g_curr, h_curr, ctx)
        if not is_member(f, ctx.generators):
            ctx.add_generator(f)
        return True

    min_color_class: None | int = None
    for color, color_class in color_classes.items():
        if len(color_class) == 4:
            min_color_class = color
            break
        elif len(color_class) > 4 and (
                min_color_class is None or len(color_class) < len(color_classes[min_color_class])):
            min_color_class = color

    if min_color_class is None:
        return False

    class_to_fix = set(color_classes[min_color_class])

    y_set = class_to_fix.intersection(set(h_curr.vertices))
    x = list(class_to_fix.difference(y_set))[0]

    if is_trivial_branch:
        y_trivial = next((y for y in y_set if y.label == x.label), None)
        if y_trivial:
            g_copy = g_curr.copy()
            h_copy = h_curr.copy()
            g_copy[x.label].color = h_copy[y_trivial.label].color = max_color + 1
            _generate_automorphism(g_copy, h_copy, ctx, is_trivial_branch=True)

        for y in y_set:
            if y.label == x.label:
                continue
            g_copy = g_curr.copy()
            h_copy = h_curr.copy()
            g_copy[x.label].color = h_copy[y.label].color = max_color + 1
            _generate_automorphism(g_copy, h_copy, ctx, is_trivial_branch=False)
        return False
    else:
        for y in y_set:
            g_copy = g_curr.copy()
            h_copy = h_curr.copy()
            g_copy[x.label].color = h_copy[y.label].color = max_color + 1
            if _generate_automorphism(g_copy, h_copy, ctx, is_trivial_branch=False):
                return True
        return False

def analyze_automorphisms(g: Graph) -> AutoAnal:
    h, mapping = g.copy_with_mapping()
    ctx = _AutSearchContext(
        g=g,
        h=h,
        mapping=mapping,
        inv_mapping={v: u for u, v in mapping.items()}
    )

    _generate_automorphism(g, h, ctx, is_trivial_branch=True)
    
    order = compute_order(ctx.generators)
    return AutoAnal(automorphism_count=order, generators=ctx.generators)
