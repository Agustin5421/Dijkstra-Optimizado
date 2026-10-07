from dijkstra_pq import dijkstra, reconstruir_camino


grafo = {
    "A": [("B", 4), ("C", 1)],
    "B": [("A", 4), ("C", 2), ("D", 1)],
    "C": [("A", 1), ("B", 2), ("D", 5)],
    "D": [("B", 1), ("C", 5)]
}


distancias, anteriores = dijkstra(grafo, "A")

print(distancias)
print(anteriores)
print(reconstruir_camino(anteriores, "A", "D"))
