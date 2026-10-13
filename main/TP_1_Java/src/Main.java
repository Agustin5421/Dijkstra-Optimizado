import adt.GrafoADT;
import algoritmos.Dijkstra;
import algoritmos.ResultadoDijkstra;
import impl.GrafoListaAdyacencia;

import java.util.Arrays;

public class Main {

    public static void main(String[] args) {
        // Mismo grafo que main.py, con A=0, B=1, C=2, D=3
        GrafoADT grafo = new GrafoListaAdyacencia(4);
        agregarNoDirigida(grafo, 0, 1, 4);
        agregarNoDirigida(grafo, 0, 2, 1);
        agregarNoDirigida(grafo, 1, 2, 2);
        agregarNoDirigida(grafo, 1, 3, 1);
        agregarNoDirigida(grafo, 2, 3, 5);

        int origen = 0;
        int destino = 3;
        ResultadoDijkstra resultado = Dijkstra.dijkstra(grafo, origen);

        System.out.println("Origen: " + origen);
        for (int v = 0; v < grafo.cantidadVertices(); v++) {
            int d = resultado.distancia(v);
            int a = resultado.anterior(v);
            System.out.println("  vertice " + v
                    + " | distancia: " + (d == ResultadoDijkstra.INF ? "inf" : d)
                    + " | anterior: " + (a == ResultadoDijkstra.SIN_ANTERIOR ? "-" : a));
        }
        System.out.println("Camino " + origen + " -> " + destino + ": "
                + Arrays.toString(resultado.reconstruirCamino(destino)));
    }

    private static void agregarNoDirigida(GrafoADT grafo, int u, int v, int peso) {
        grafo.agregarArista(u, v, peso);
        grafo.agregarArista(v, u, peso);
    }
}
