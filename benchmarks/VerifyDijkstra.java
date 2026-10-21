import adt.GrafoADT;
import algoritmos.*;
import impl.GrafoListaAdyacencia;
import java.util.*;

/** Oráculo independiente long/Bellman-Ford para dominio válido y sondas de int. */
public class VerifyDijkstra {
    private static void verify(int n, int[][] edges, int source) {
        GrafoADT graph = new GrafoListaAdyacencia(n);
        for (int[] edge : edges) {
            graph.agregarArista(edge[0], edge[1], edge[2]);
        }
        long[] expected = new long[n];
        Arrays.fill(expected, Long.MAX_VALUE / 4);
        expected[source] = 0;
        for (int step = 1; step < n; step++) {
            for (int[] edge : edges) {
                expected[edge[1]] = Math.min(expected[edge[1]], expected[edge[0]] + edge[2]);
            }
        }
        for (ResultadoDijkstra result : new ResultadoDijkstra[] {
                Dijkstra.dijkstra(graph, source), DijkstraNormal.dijkstra(graph, source)}) {
            for (int v = 0; v < n; v++) {
                long distance = expected[v] == Long.MAX_VALUE / 4 ? Integer.MAX_VALUE : expected[v];
                if (result.distancia(v) != distance) {
                    throw new AssertionError("Esperado " + distance + ", recibido " + result.distancia(v));
                }
                int[] path = result.reconstruirCamino(v);
                if (distance == Integer.MAX_VALUE) {
                    if (path.length != 0) { throw new AssertionError("Inaccesible con camino"); }
                } else {
                    if (path.length == 0 || path[0] != source || path[path.length - 1] != v
                            || path.length > n) { throw new AssertionError("Camino inválido"); }
                    long cost = 0;
                    for (int p = 1; p < path.length; p++) {
                        int minimum = Integer.MAX_VALUE;
                        for (int[] edge : edges) {
                            if (edge[0] == path[p - 1] && edge[1] == path[p]) {
                                minimum = Math.min(minimum, edge[2]);
                            }
                        }
                        cost += minimum;
                    }
                    if (cost != distance) { throw new AssertionError("Costo del camino incorrecto"); }
                }
            }
        }
    }

    public static void main(String[] args) {
        if (args.length == 0) {
            verify(1, new int[][] {}, 0);
            verify(4, new int[][] {{0,0,0},{0,1,0},{1,0,0},{0,2,10},{1,2,2},{0,2,5}}, 0);
            for (int seed = 0; seed < 100; seed++) {
                Random rng = new Random(seed);
                int n = 1 + rng.nextInt(14);
                List<int[]> edges = new ArrayList<>();
                for (int u = 0; u < n; u++) {
                    for (int v = 0; v < n; v++) {
                        if (rng.nextDouble() < 0.25) { edges.add(new int[] {u, v, rng.nextInt(41)}); }
                    }
                }
                verify(n, edges.toArray(new int[0][]), rng.nextInt(n));
            }
            System.out.println("102 grafos Java: distancias y caminos correctos en ambas variantes");
        } else if (args[0].equals("overflow")) {
            verify(3, new int[][] {{0,1,2000000000},{1,2,2000000000}}, 0);
        } else if (args[0].equals("sentinel")) {
            GrafoADT graph = new GrafoListaAdyacencia(2);
            graph.agregarArista(0, 1, Integer.MAX_VALUE);
            for (ResultadoDijkstra result : new ResultadoDijkstra[] {
                    Dijkstra.dijkstra(graph, 0), DijkstraNormal.dijkstra(graph, 0)}) {
                if (result.reconstruirCamino(1).length != 2) {
                    throw new AssertionError("Distancia válida MAX_VALUE confundida con infinito");
                }
            }
        }
    }
}
