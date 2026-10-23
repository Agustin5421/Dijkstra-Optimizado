package algoritmos;

public class ResultadoDijkstra {

    public static final int INF = Integer.MAX_VALUE;
    public static final int SIN_ANTERIOR = -1;

    private final int origen;
    private final int[] distancias;
    private final int[] anteriores;

    public ResultadoDijkstra(int origen, int[] distancias, int[] anteriores) {
        this.origen = origen;
        this.distancias = distancias;
        this.anteriores = anteriores;
    }

    /** Distancia mínima desde el origen, o INF si v es inaccesible. */
    public int distancia(int v) {
        return distancias[v];
    }

    /** Predecesor de v en el camino mínimo, o SIN_ANTERIOR. */
    public int anterior(int v) {
        return anteriores[v];
    }

    /** Camino desde el origen hasta destino; vacío si es inaccesible. */
    public int[] reconstruirCamino(int destino) {
        if (distancias[destino] == INF) {
            return new int[0];
        }

        int largo = 0;
        for (int actual = destino; actual != SIN_ANTERIOR; actual = anteriores[actual]) {
            largo++;
        }

        int[] camino = new int[largo];
        int i = largo - 1;
        for (int actual = destino; actual != SIN_ANTERIOR; actual = anteriores[actual]) {
            camino[i--] = actual;
        }

        if (camino[0] != origen) {
            return new int[0];
        }
        return camino;
    }
}
