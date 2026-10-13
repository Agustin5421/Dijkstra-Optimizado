package algoritmos;

import adt.Arista;
import adt.ColaPrioridadADT;
import adt.GrafoADT;
import impl.ColaPrioridadHeap;

public class Dijkstra {

    /**
     * Calcula las distancias mínimas desde origen.
     * Precondición: pesos no negativos. Complejidad: O((V + E) log V).
     */
    public static ResultadoDijkstra dijkstra(GrafoADT grafo, int origen) {
        int n = grafo.cantidadVertices();
        int[] distancias = new int[n];
        int[] anteriores = new int[n];

        for (int v = 0; v < n; v++) {
            distancias[v] = ResultadoDijkstra.INF;
            anteriores[v] = ResultadoDijkstra.SIN_ANTERIOR;
        }
        distancias[origen] = 0;

        ColaPrioridadADT pq = new ColaPrioridadHeap();
        pq.acolar(origen, 0);

        while (!pq.estaVacia()) {
            int u = pq.primero();
            int distanciaActual = pq.prioridadPrimero();
            pq.desacolar();

            // Si ya encontramos una distancia mejor, ignoramos esta entrada
            if (distanciaActual > distancias[u]) {
                continue;
            }

            for (Arista arista : grafo.adyacentes(u)) {
                int v = arista.getDestino();
                int nuevaDistancia = distanciaActual + arista.getPeso();

                if (nuevaDistancia < distancias[v]) {
                    distancias[v] = nuevaDistancia;
                    anteriores[v] = u;

                    pq.acolar(v, nuevaDistancia);
                }
            }
        }

        return new ResultadoDijkstra(origen, distancias, anteriores);
    }
}
