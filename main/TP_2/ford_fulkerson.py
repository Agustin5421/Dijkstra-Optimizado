import heapq


def construir_residual(grafo):
    residual = {u: {} for u in grafo}

    for u in grafo:
        for v, capacidad in grafo[u]:
            residual.setdefault(v, {})
            residual[u][v] = residual[u].get(v, 0) + capacidad
            # Arista inversa: empieza en 0, crece cuando mandamos flujo por u -> v
            residual[v].setdefault(u, 0)

    return residual


def buscar_camino(residual, origen, destino):
    # Como Dijkstra, pero en vez de la menor distancia buscamos el camino
    # que permite mandar el mayor valor (el cuello de botella más grande)
    mejor = {origen: float("inf")}
    anteriores = {origen: None}

    # (-valor, vértice): heapq es un min-heap, negamos para sacar el mayor
    pq = [(-float("inf"), origen)]

    while pq:
        valor_actual, u = heapq.heappop(pq)
        valor_actual = -valor_actual

        if u == destino:
            break

        for v, capacidad in residual[u].items():
            nuevo_valor = min(valor_actual, capacidad)

            if nuevo_valor > mejor.get(v, 0):
                mejor[v] = nuevo_valor
                anteriores[v] = u
                heapq.heappush(pq, (-nuevo_valor, v))

    if destino not in anteriores:
        return None

    return reconstruir_camino(anteriores, origen, destino)


def reconstruir_camino(anteriores, origen, destino):
    camino = []
    actual = destino

    while actual is not None:
        camino.append(actual)
        actual = anteriores[actual]

    camino.reverse()

    return camino


def ford_fulkerson(grafo, fuente, sumidero):
    residual = construir_residual(grafo)
    flujo_maximo = 0
    caminos = []

    while True:
        camino = buscar_camino(residual, fuente, sumidero)
        if camino is None:
            break

        aristas = list(zip(camino, camino[1:]))

        # El cuello de botella es la menor capacidad residual del camino
        cuello = min(residual[u][v] for u, v in aristas)

        for u, v in aristas:
            residual[u][v] -= cuello
            residual[v][u] += cuello

        flujo_maximo += cuello
        caminos.append((camino, cuello))

    return flujo_maximo, caminos


if __name__ == "__main__":
    grafo = {
        "A": [("B", 8), ("C", 5), ("D", 9)],
        "B": [("E", 9)],
        "C": [("B", 3), ("F", 4)],
        "D": [("C", 6), ("G", 2)],
        "E": [("F", 3), ("H", 8)],
        "F": [("H", 5)],
        "G": [("F", 2), ("H", 9)],
        "H": [],
    }

    flujo, caminos = ford_fulkerson(grafo, "A", "H")

    for i, (camino, cuello) in enumerate(caminos, start=1):
        print(f"Iteración {i}: {' -> '.join(camino)}  (+{cuello})")

    print(f"Flujo máximo: {flujo}")
