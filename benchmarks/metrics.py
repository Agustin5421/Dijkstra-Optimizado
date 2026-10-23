"""Contadores fuera de la región cronometrada; no sustituyen al código real."""
import heapq


def count_operations(graph, optimized):
    distances = dict.fromkeys(graph, float("inf"))
    distances[0] = 0
    stats = dict(scans=0, edges=0, updates=0, pushes=0, pops=0,
                 stale=0, peak_queue=0, reached=0)
    pending = set(graph)
    queue = [(0, 0)]
    if optimized:
        stats["pushes"] = 1
        stats["peak_queue"] = 1
    running = True
    while running:
        u = None
        minimum = float("inf")
        valid = True
        if optimized:
            running = bool(queue)
            if running:
                minimum, u = heapq.heappop(queue)
                stats["pops"] += 1
                valid = minimum <= distances[u]
                stats["stale"] += int(valid is False)
        else:
            for v in pending:
                stats["scans"] += 1
                if distances[v] < minimum:
                    u, minimum = v, distances[v]
            running = u is not None
            if running:
                pending.remove(u)
        if running and valid:
            stats["reached"] += 1
            for v, weight in graph[u]:
                stats["edges"] += 1
                candidate = minimum + weight
                if candidate < distances[v]:
                    distances[v] = candidate
                    stats["updates"] += 1
                    if optimized:
                        heapq.heappush(queue, (candidate, v))
                        stats["pushes"] += 1
                        stats["peak_queue"] = max(stats["peak_queue"], len(queue))
    return distances, stats
