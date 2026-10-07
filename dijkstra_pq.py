import heapq

def dijkstra(grafo, origen):
    distancias = {v: float("inf") for v in grafo}
    anteriores = {v: None for v in grafo}

    distancias[origen] = 0

    # (distancia, vértice)
    pq = [(0, origen)]

    while pq:
        distancia_actual, u = heapq.heappop(pq)

        # Si ya encontramos una distancia mejor, ignoramos esta entrada
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
