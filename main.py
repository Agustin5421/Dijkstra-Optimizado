import heapq


grafo = {
    "A": [("B", 4), ("C", 1)],
    "B": [("A", 4), ("C", 2), ("D", 1)],
    "C": [("A", 1), ("B", 2), ("D", 5)],
    "D": [("B", 1), ("C", 5)]
}


def dijkstra(grafo, origen):
    distancias = {v: float("inf") for v in grafo}
    anteriores = {v: None for v in grafo}

    distancias[origen] = 0

    pq = [(0, origen)]

    while pq:
        distancia_actual, u = heapq.heappop(pq)

        if distancia_actual > distancias[u]:
            continue

        for v, peso in grafo[u]:
            nueva_distancia = distancia_actual + peso

            if nueva_distancia < distancias[v]:
                distancias[v] = nueva_distancia
                anteriores[v] = u

                heapq.heappush(pq, (nueva_distancia, v))

    return distancias, anteriores


distancias, anteriores = dijkstra(grafo, "A")

print(distancias)
print(anteriores)
