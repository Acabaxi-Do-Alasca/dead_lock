"""Desenho do Grafo de Alocação de Recursos (RAG) com matplotlib + networkx.

Layout fixo em duas colunas (processos à esquerda, recursos à direita) para
que o grafo não "pule" a cada redesenho -- importante para acompanhar a
simulação ao vivo. Arestas de alocação (Recurso -> Processo) em preto,
arestas de requisição pendente (Processo -> Recurso) tracejadas em vermelho.
Se as arestas pendentes fecharem um ciclo, ele é destacado.
"""

import networkx as nx

from core.models import ProcessState

STATE_COLORS = {
    ProcessState.READY: "#8BC34A",
    ProcessState.RUNNING: "#4CAF50",
    ProcessState.BLOCKED: "#FFC107",
    ProcessState.FINISHED: "#BDBDBD",
}

RESOURCE_COLOR = "#90CAF9"
CYCLE_COLOR = "#E53935"


def _find_cycle_edges(state, outstanding_requests):
    """Retorna o conjunto de arestas (u, v) que participam de algum ciclo,
    considerando alocação (R->P) e requisição pendente (P->R)."""
    graph = nx.DiGraph()
    n_res = len(state.resources)

    for i, p in enumerate(state.processes):
        for j, r in enumerate(state.resources):
            if state.allocation[i][j] > 0:
                graph.add_edge(("R", j), ("P", i))

    for i, p in enumerate(state.processes):
        req = outstanding_requests.get(p.pid, [0] * n_res)
        for j in range(n_res):
            if req[j] > 0:
                graph.add_edge(("P", i), ("R", j))

    cycle_edges = set()
    try:
        for cycle in nx.simple_cycles(graph):
            for k in range(len(cycle)):
                cycle_edges.add((cycle[k], cycle[(k + 1) % len(cycle)]))
    except nx.NetworkXNoCycle:
        pass
    return cycle_edges


def draw_rag(ax, engine) -> bool:
    """Redesenha o grafo no eixo `ax`. Retorna True se um ciclo foi encontrado."""
    ax.clear()
    state = engine.state
    n_proc = len(state.processes)
    n_res = len(state.resources)

    def column_ys(n):
        if n == 1:
            return [0.5]
        return [0.9 - 0.8 * k / (n - 1) for k in range(n)]

    proc_ys = column_ys(n_proc)
    res_ys = column_ys(n_res)
    proc_pos = {("P", i): (0.15, proc_ys[i]) for i in range(n_proc)}
    res_pos = {("R", j): (0.85, res_ys[j]) for j in range(n_res)}

    cycle_edges = _find_cycle_edges(state, engine.outstanding_requests)
    has_cycle = len(cycle_edges) > 0

    # arestas de alocação: Recurso -> Processo
    for i in range(n_proc):
        for j in range(n_res):
            amount = state.allocation[i][j]
            if amount <= 0:
                continue
            edge_in_cycle = (("R", j), ("P", i)) in cycle_edges
            _draw_arrow(
                ax,
                res_pos[("R", j)],
                proc_pos[("P", i)],
                color=CYCLE_COLOR if edge_in_cycle else "black",
                style="solid",
                label=str(amount) if amount > 1 else None,
            )

    # arestas de requisição pendente: Processo -> Recurso
    for i, p in enumerate(state.processes):
        req = engine.outstanding_requests.get(p.pid, [0] * n_res)
        for j in range(n_res):
            if req[j] <= 0:
                continue
            edge_in_cycle = (("P", i), ("R", j)) in cycle_edges
            _draw_arrow(
                ax,
                proc_pos[("P", i)],
                res_pos[("R", j)],
                color=CYCLE_COLOR if edge_in_cycle else "#E57373",
                style="dashed",
                label=str(req[j]) if req[j] > 1 else None,
            )

    # nós de recurso (quadrados)
    for j, r in enumerate(state.resources):
        x, y = res_pos[("R", j)]
        ax.scatter([x], [y], s=1800, marker="s", color=RESOURCE_COLOR, edgecolors="black", zorder=3)
        ax.text(x, y, f"{r.name}\n{state.available[j]}/{r.total_instances}",
                ha="center", va="center", fontsize=8, zorder=4)

    # nós de processo (círculos)
    for i, p in enumerate(state.processes):
        x, y = proc_pos[("P", i)]
        color = STATE_COLORS.get(p.state, "#CCCCCC")
        ax.scatter([x], [y], s=1800, marker="o", color=color, edgecolors="black", zorder=3)
        ax.text(x, y, p.name, ha="center", va="center", fontsize=9, fontweight="bold", zorder=4)

    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.axis("off")
    title = "Grafo de Alocação de Recursos"
    if has_cycle:
        title += "  --  CICLO DETECTADO (possível deadlock)"
    ax.set_title(title, fontsize=10, color=CYCLE_COLOR if has_cycle else "black")

    return has_cycle


def _draw_arrow(ax, start, end, color, style, label=None):
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops=dict(
            arrowstyle="-|>",
            color=color,
            linestyle=style,
            shrinkA=28,
            shrinkB=28,
            linewidth=1.6,
        ),
        zorder=2,
    )
    if label:
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        ax.text(mid_x, mid_y, label, fontsize=8, color=color, ha="center", va="center",
                bbox=dict(boxstyle="round", fc="white", ec="none", alpha=0.8), zorder=5)
