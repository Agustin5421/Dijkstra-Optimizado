"""Grafos dirigidos reproducibles. E cuenta entradas de adyacencia."""
import random


LABELS = {
    "tiny": "Pequeños",
    "chain": "Cadena",
    "star": "Estrella",
    "sparse": "Disperso aleatorio",
    "grid": "Grilla bidireccional",
    "disconnected": "10% alcanzable",
    "isolated": "Origen aislado",
    "dense": "Denso aleatorio",
    "ties": "Completo, pesos iguales",
    "zero": "Disperso, pesos cero",
    "adversarial": "Muchas mejoras",
    "parallel": "Aristas paralelas decrecientes",
}

SIZES = {
    "tiny": [1, 4, 8, 16],
    "chain": [128, 512, 2048],
    "star": [128, 512, 2048],
    "sparse": [128, 512, 2048],
    "grid": [144, 529, 2025],
    "disconnected": [128, 512, 2048],
    "isolated": [128, 512, 2048],
    "dense": [64, 128, 256],
    "ties": [64, 128, 256],
    "zero": [128, 512, 2048],
    "adversarial": [32, 64, 128, 256],
    "parallel": [128, 2048, 16384],
}


def make_graph(family, size, seed):
    rng = random.Random(seed)
    n = 2 if family == "parallel" else size
    graph = {v: [] for v in range(n)}
    if family in ("tiny", "chain", "sparse", "zero", "disconnected"):
        active = max(1, n // 10) if family == "disconnected" else n
        for v in range(active - 1):
            graph[v].append((v + 1, rng.randint(1, 100)))
        if family in ("sparse", "zero", "disconnected"):
            for u in range(active):
                targets = rng.sample(range(active), min(4, active))
                for v in targets:
                    if u != v:
                        graph[u].append((v, 0 if family == "zero" else rng.randint(1, 100)))
    elif family == "star":
        graph[0] = [(v, rng.randint(1, 100)) for v in range(1, n)]
    elif family == "grid":
        side = int(n ** 0.5)
        for u in range(n):
            for v in (u + 1, u + side):
                horizontal = v == u + 1 and u // side == v // side
                if v < n and (horizontal or v == u + side):
                    weight = rng.randint(1, 100)
                    graph[u].append((v, weight))
                    graph[v].append((u, weight))
    elif family in ("dense", "ties"):
        for u in range(n):
            graph[u] = [(v, 1 if family == "ties" else rng.randint(1, 1000))
                        for v in range(n) if u != v]
    elif family == "adversarial":
        # k intermediarios salen antes que los destinos. Cada uno mejora
        # TODOS los destinos: Θ(E) entradas vivas/obsoletas en el heap.
        k = (n - 1) // 2
        graph[0] = [(u, u) for u in range(1, k + 1)]
        for u in range(1, k + 1):
            graph[u] = [(v, 3 * k - 2 * u) for v in range(k + 1, n)]
    elif family == "parallel":
        graph[0] = [(1, weight) for weight in range(size, 0, -1)]
    elif family != "isolated":
        raise ValueError(f"Familia desconocida: {family}")
    return graph
