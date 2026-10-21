"""Dijkstra clásico: selección lineal del mínimo, sin cola de prioridad.

Misma representación y contrato que dijkstra_pq: todos los destinos deben
ser claves del grafo, el origen debe existir y los pesos deben ser no negativos.
"""


def dijkstra(grafo, origen):
    distancias = {v: float("inf") for v in grafo}
    anteriores = {v: None for v in grafo}
    pendientes = set(grafo)
    distancias[origen] = 0

    while pendientes:
        u = None
        minimo = float("inf")
        for v in pendientes:
            if distancias[v] < minimo:
                u = v
                minimo = distancias[v]

        if u is None:
            break

        pendientes.remove(u)
        for v, peso in grafo[u]:
            nueva_distancia = minimo + peso
            if nueva_distancia < distancias[v]:
                distancias[v] = nueva_distancia
                anteriores[v] = u

    return distancias, anteriores
