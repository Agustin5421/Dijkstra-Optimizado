import math
import random
import pytest

from dijkstra_normal import dijkstra as normal
from dijkstra_pq import dijkstra as heap, reconstruir_camino
from scenarios import SIZES, make_graph
from metrics import count_operations


def bellman_ford(graph, source):
    """Oráculo independiente: relajaciones globales, sin selección de mínimos."""
    distances = dict.fromkeys(graph, math.inf)
    distances[source] = 0
    for _ in range(len(graph) - 1):
        for u, edges in graph.items():
            for v, weight in edges:
                distances[v] = min(distances[v], distances[u] + weight)
    return distances


def check_paths(graph, source, distances, previous):
    for target in graph:
        path = reconstruir_camino(previous, source, target)
        if math.isinf(distances[target]):
            assert path == []
        else:
            assert path[0] == source and path[-1] == target
            assert len(path) == len(set(path))
            weight = sum(min(w for v, w in graph[u] if v == nxt)
                         for u, nxt in zip(path, path[1:]))
            assert weight == distances[target]


CASES = [
    {0: []},
    {0: [], 1: []},
    {0: [(0, 0), (1, 0)], 1: [(0, 0)]},
    {0: [(1, 10), (2, 1)], 1: [], 2: [(1, 1)]},
    {0: [(1, 4), (1, 2)], 1: []},
    {0: [(1, 1), (2, 1)], 1: [(3, 1)], 2: [(3, 1)], 3: []},
    {0: [(1, 2**63)], 1: [(2, 2**63)], 2: []},
    {"A": [("B", 1.5)], "B": [("C", 0.25)], "C": []},
]


@pytest.mark.parametrize("algorithm", [normal, heap])
@pytest.mark.parametrize("graph", CASES)
def test_bordes_y_caminos(algorithm, graph):
    for source in graph:
        distances, previous = algorithm(graph, source)
        assert distances == bellman_ford(graph, source)
        check_paths(graph, source, distances, previous)


@pytest.mark.parametrize("seed", range(100))
def test_aleatorios_con_oraculo_independiente(seed):
    rng = random.Random(seed)
    n = rng.randint(1, 14)
    graph = {u: [(v, rng.randint(0, 40)) for v in range(n)
                 if rng.random() < 0.25] for u in range(n)}
    source = rng.randrange(n)
    expected = bellman_ford(graph, source)
    for algorithm in (normal, heap):
        distances, previous = algorithm(graph, source)
        assert distances == expected
        check_paths(graph, source, distances, previous)


@pytest.mark.parametrize("family", SIZES)
def test_generadores_y_contadores(family):
    graph = make_graph(family, SIZES[family][0], 17)
    expected = bellman_ford(graph, 0)
    for optimized, algorithm in ((False, normal), (True, heap)):
        distances, previous = algorithm(graph, 0)
        counted, stats = count_operations(graph, optimized)
        assert distances == counted == expected
        check_paths(graph, 0, distances, previous)
        assert stats["reached"] == sum(math.isfinite(d) for d in expected.values())


def test_familia_adversaria_genera_cola_cuadratica():
    graph = make_graph("adversarial", 128, 0)
    _, stats = count_operations(graph, True)
    assert stats["stale"] > 3000
    assert stats["peak_queue"] > 3000


def test_orden_de_aristas_cambia_trabajo_pero_no_distancias():
    descending = make_graph("parallel", 512, 0)
    ascending = {0: list(reversed(descending[0])), 1: []}
    d1, stats1 = count_operations(descending, True)
    d2, stats2 = count_operations(ascending, True)
    assert d1 == d2 == normal(descending, 0)[0] == heap(ascending, 0)[0]
    assert stats1["stale"] == 511
    assert stats2["stale"] == 0
    assert stats1["peak_queue"] == 512
    assert stats2["peak_queue"] == 1


@pytest.mark.xfail(strict=True, reason="Contrato actual: el heap compara etiquetas al empatar")
def test_heap_etiquetas_heterogeneas_con_empate():
    # Los dict admiten estas claves; heapq intenta comparar int con str.
    graph = {0: [(1, 1), ("B", 1)], 1: [], "B": []}
    assert heap(graph, 0)[0] == normal(graph, 0)[0]
