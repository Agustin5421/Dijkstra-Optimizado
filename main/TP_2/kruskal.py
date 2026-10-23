def matriz_a_aristas(grafo):
    n = len(grafo)
    edges = []
    for i in range(n):
        for j in range(i+1, n):  # solo arriba de la diagonal
            if grafo[i][j] != 0:
                edges.append((grafo[i][j], i, j))  # (peso, u, v)
    return edges


def Kruskal(grafo):
    n = len(grafo)
    edges = matriz_a_aristas(grafo)

    # Ordenar por peso
    edges.sort()  # ordena por el primer elemento de la tupla

    # Inicializar Union-Find
    parent = [i for i in range(n)]
    rank = [0] * n

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        rx = find(x)
        ry = find(y)

        if rx == ry:
            return False  # ya estaban unidos → ciclo

        if rank[rx] < rank[ry]:
            parent[rx] = ry
        elif rank[rx] > rank[ry]:
            parent[ry] = rx
        else:
            parent[ry] = rx
            rank[rx] += 1

        return True

    # Construir el MST
    mst = []
    for peso, u, v in edges:
        if union(u, v):
            mst.append((u, v, peso))
    return mst
##############################
mi_grafo = [
    [0, 1, 4, 0, 2],
    [1, 0, 0, 3, 3],
    [4, 0, 0, 1, 1],
    [0, 3, 1, 0, 2],
    [2, 3, 1, 2, 0]
]
mst = Kruskal(mi_grafo)
for componente in mst:
  print(componente)
