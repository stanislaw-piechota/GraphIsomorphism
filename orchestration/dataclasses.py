from dataclasses import dataclass, field


@dataclass
class IsomorphismAnalResult:
    isomorphic_graphs: list[list[int]]
    automorphism_counts: list[int]
    was_counting_automorphism: bool

    def __str__(self) -> str:
        if self.was_counting_automorphism:
            lines = ["Sets of isomorphic graphs and automorphisms:"]
            for graphs, count in zip(self.isomorphic_graphs, self.automorphism_counts):
                lines.append(f" {graphs}: {count}")
            return "\n".join(lines)
        else:
            lines = ["Sets of isomorphic graphs"]
            for graphs in self.isomorphic_graphs:
                lines.append(f" {graphs}")
            return "\n".join(lines)

@dataclass
class AutomorphismsAnalResult:
    list_of_automorphism_counts: list[int] = field(default_factory=list)

    def __str__(self) -> str:
        lines = ["Automorphism Counts:"]
        for graph_idx, automorphism_count in enumerate(self.list_of_automorphism_counts):
            lines.append(f"  Graph {graph_idx} Automorphisms: {automorphism_count}")
        return "\n".join(lines)