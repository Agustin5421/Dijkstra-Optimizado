import heapq

import dijkstra_pq
from dijkstra_pq import dijkstra, reconstruir_camino


INF = float("inf")


def test_grafo_simple():
    grafo = {
        "A": [("B", 4), ("C", 1)],
        "B": [("A", 4), ("C", 2), ("D", 1)],
        "C": [("A", 1), ("B", 2), ("D", 5)],
        "D": [("B", 1), ("C", 5)]
    }

    distancias, anteriores = dijkstra(grafo, "A")

    assert distancias == {"A": 0, "B": 3, "C": 1, "D": 4}
    assert anteriores == {"A": None, "B": "C", "C": "A", "D": "B"}


def test_varios_caminos_elige_el_mas_corto():
    grafo = {
        "A": [("B", 2), ("C", 1), ("D", 10)],
        "B": [("D", 3)],
        "C": [("D", 6)],
        "D": []
    }

    distancias, anteriores = dijkstra(grafo, "A")

    assert distancias["D"] == 5
    assert anteriores["D"] == "B"


def test_nodo_inaccesible():
    grafo = {
        "A": [("B", 1)],
        "B": [],
        "C": [("A", 1)]
    }

    distancias, anteriores = dijkstra(grafo, "A")

    assert distancias["C"] == INF
    assert anteriores["C"] is None
    assert reconstruir_camino(anteriores, "A", "C") == []


def test_actualiza_distancia_ya_descubierta():
    grafo = {
        "A": [("B", 10), ("C", 1)],
        "B": [],
        "C": [("B", 2)]
    }

    distancias, anteriores = dijkstra(grafo, "A")

    assert distancias["B"] == 3
    assert anteriores["B"] == "C"


def test_entradas_repetidas_en_la_cola(monkeypatch):
    grafo = {
        "A": [("D", 10), ("B", 1)],
        "B": [("D", 5), ("C", 1)],
        "C": [("D", 1)],
        "D": []
    }

    insertados = []
    heappush_original = heapq.heappush

    def heappush_registrando(pq, entrada):
        insertados.append(entrada)
        heappush_original(pq, entrada)

    monkeypatch.setattr(dijkstra_pq.heapq, "heappush", heappush_registrando)

    distancias, anteriores = dijkstra(grafo, "A")

    entradas_de_d = [d for d, v in insertados if v == "D"]

    assert entradas_de_d == [10, 6, 3]
    assert distancias["D"] == 3
    assert anteriores["D"] == "C"


def test_reconstruccion_del_camino():
    grafo = {
        "A": [("B", 4), ("C", 1)],
        "B": [("A", 4), ("C", 2), ("D", 1)],
        "C": [("A", 1), ("B", 2), ("D", 5)],
        "D": [("B", 1), ("C", 5)]
    }

    _, anteriores = dijkstra(grafo, "A")

    assert reconstruir_camino(anteriores, "A", "D") == ["A", "C", "B", "D"]


def test_camino_al_mismo_origen():
    grafo = {
        "A": [("B", 1)],
        "B": []
    }

    _, anteriores = dijkstra(grafo, "A")

    assert reconstruir_camino(anteriores, "A", "A") == ["A"]
