package algoritmos;

import adt.Arista;
import adt.GrafoADT;

/** Dijkstra clásico O(V² + E), con el mismo contrato numérico que Dijkstra. */
public class DijkstraNormal {
    public static ResultadoDijkstra dijkstra(GrafoADT grafo, int origen) {
        int n = grafo.cantidadVertices();
        int[] distancias = new int[n];
        int[] anteriores = new int[n];
        boolean[] visitados = new boolean[n];
        java.util.Arrays.fill(distancias, ResultadoDijkstra.INF);
        java.util.Arrays.fill(anteriores, ResultadoDijkstra.SIN_ANTERIOR);
        distancias[origen] = 0;

        boolean alcanzables = true;
        for (int paso = 0; paso < n && alcanzables; paso++) {
            int u = -1;
            int minimo = ResultadoDijkstra.INF;
            for (int v = 0; v < n; v++) {
                if (visitados[v] == false && distancias[v] < minimo) {
                    minimo = distancias[v];
                    u = v;
                }
            }
            alcanzables = u >= 0;
            if (alcanzables) {
                visitados[u] = true;
                for (Arista arista : grafo.adyacentes(u)) {
                    int v = arista.getDestino();
                    int candidata = minimo + arista.getPeso();
                    if (candidata < distancias[v]) {
                        distancias[v] = candidata;
                        anteriores[v] = u;
                    }
                }
            }
        }
        return new ResultadoDijkstra(origen, distancias, anteriores);
    }
}
